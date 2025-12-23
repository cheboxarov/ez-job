"""Use case для обработки автооткликов на вакансии."""

from __future__ import annotations

import asyncio
import uuid
from typing import Dict

from loguru import logger

from domain.entities.filtered_vacancy_list import FilteredVacancyListItem
from domain.entities.resume import Resume
from domain.entities.resume_filter_settings import ResumeFilterSettings
from domain.entities.user_hh_auth_data import UserHhAuthData
from domain.exceptions.subscription_limit_exceeded import SubscriptionLimitExceededError
from domain.interfaces.cover_letter_generator_port import CoverLetterGeneratorPort
from domain.interfaces.resume_filter_settings_repository_port import (
    ResumeFilterSettingsRepositoryPort,
)
from domain.interfaces.resume_repository_port import ResumeRepositoryPort
from domain.interfaces.user_hh_auth_data_repository_port import (
    UserHhAuthDataRepositoryPort,
)
from domain.interfaces.hh_client_port import HHClientPort
from domain.use_cases.generate_test_answers import GenerateTestAnswersUseCase
from domain.use_cases.get_vacancy_test import GetVacancyTestUseCase
from domain.use_cases.search_and_get_filtered_vacancy_list import (
    SearchAndGetFilteredVacancyListUseCase,
)
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase


class AutoReplyDisabledError(Exception):
    """Исключение, которое бросается когда автоотклик выключен во время обработки."""


class ProcessAutoRepliesUseCase:
    """Use case для автоматической обработки откликов на вакансии.

    Для каждого резюме с включенным автооткликом:
    1. Получает подходящие вакансии (до 200 штук)
    2. Фильтрует вакансии с confidence >= 0.5 (50%)
    3. Сортирует по confidence (сначала самые подходящие)
    4. Для каждой вакансии генерирует письмо и отправляет отклик
    5. Для вакансий с тестами получает тест, генерирует ответы и отправляет их с откликом
    6. Делает паузу 30 секунд между откликами
    """

    def __init__(
        self,
        resume_repository: ResumeRepositoryPort,
        user_hh_auth_data_repository: UserHhAuthDataRepositoryPort,
        resume_filter_settings_repository: ResumeFilterSettingsRepositoryPort,
        search_and_get_filtered_vacancy_list_uc: SearchAndGetFilteredVacancyListUseCase,
        cover_letter_generator: CoverLetterGeneratorPort,
        create_unit_of_work_factory,
        respond_to_vacancy_uc,
        hh_client: HHClientPort,
        generate_test_answers_uc: GenerateTestAnswersUseCase,
        check_subscription_uc=None,
        increment_response_count_uc=None,
        max_vacancies_per_resume: int = 200,
        delay_between_replies_seconds: int = 30,
    ) -> None:
        """Инициализация use case.

        Args:
            resume_repository: Репозиторий резюме.
            user_hh_auth_data_repository: Репозиторий auth данных пользователя.
            resume_filter_settings_repository: Репозиторий настроек фильтров резюме.
            search_and_get_filtered_vacancy_list_uc: Use case для поиска вакансий.
            cover_letter_generator: Генератор сопроводительных писем.
            create_unit_of_work_factory: Фабрика для создания UnitOfWork (для каждого отклика отдельная транзакция).
            respond_to_vacancy_uc: Use case для отправки отклика в HH API.
            hh_client: Клиент для работы с HeadHunter API (для получения теста вакансии).
            generate_test_answers_uc: Use case для генерации ответов на тест вакансии.
            check_subscription_uc: Use case для проверки подписки (опционально).
            increment_response_count_uc: Use case для инкремента счетчика откликов (опционально).
            max_vacancies_per_resume: Максимальное количество вакансий для обработки на одно резюме.
            delay_between_replies_seconds: Задержка между откликами в секундах.
        """
        self._resume_repository = resume_repository
        self._user_hh_auth_data_repository = user_hh_auth_data_repository
        self._resume_filter_settings_repository = resume_filter_settings_repository
        self._search_and_get_filtered_vacancy_list_uc = search_and_get_filtered_vacancy_list_uc
        self._cover_letter_generator = cover_letter_generator
        self._create_unit_of_work_factory = create_unit_of_work_factory
        self._respond_to_vacancy_uc = respond_to_vacancy_uc
        self._hh_client = hh_client
        self._generate_test_answers_uc = generate_test_answers_uc
        self._check_subscription_uc = check_subscription_uc
        self._increment_response_count_uc = increment_response_count_uc
        self._max_vacancies_per_resume = max_vacancies_per_resume
        self._delay_between_replies_seconds = delay_between_replies_seconds

    async def execute(self) -> None:
        """Выполнить обработку автооткликов для всех активных резюме."""
        # 1. Получаем все резюме с включенным автооткликом
        resumes = await self._resume_repository.get_all_active_auto_reply_resumes()
        logger.info(f"Найдено резюме с автооткликом: {len(resumes)}")

        for resume in resumes:
            try:
                await self._process_resume(resume)
            except Exception as exc:
                logger.error(
                    f"Ошибка при обработке резюме {resume.id}: {exc}",
                    exc_info=True,
                )
                # Продолжаем обработку других резюме даже при ошибке

    async def process_single_resume(self, resume: Resume) -> None:
        """Обработать одно резюме (публичный метод для использования в worker).
        
        Args:
            resume: Резюме для обработки.
        """
        await self._process_resume(resume)

    async def _process_resume(self, resume: Resume) -> None:
        """Обработать одно резюме: найти вакансии и откликнуться.

        Args:
            resume: Резюме для обработки.
        """
        logger.info(f"Обработка резюме {resume.id}")

        # 0. Проверяем лимит подписки перед началом обработки
        if self._check_subscription_uc is not None:
            try:
                user_subscription, plan = await self._check_subscription_uc.execute(
                    resume.user_id
                )
                if user_subscription.responses_count >= plan.response_limit:
                    logger.info(
                        f"Лимит откликов для пользователя {resume.user_id} исчерпан: "
                        f"{user_subscription.responses_count}/{plan.response_limit}. "
                        f"Пропускаем резюме {resume.id}"
                    )
                    return
            except ValueError as exc:
                # Если подписка не найдена, логируем и продолжаем
                logger.warning(
                    f"Не удалось проверить лимит подписки для user_id={resume.user_id}: {exc}. "
                    "Продолжаем без проверки лимита."
                )

        # 1. Получаем auth данные пользователя
        auth_data = await self._user_hh_auth_data_repository.get_by_user_id(resume.user_id)
        if not auth_data:
            logger.warning(
                f"Для резюме {resume.id} не найдены auth данные пользователя {resume.user_id}"
            )
            return

        # 2. Получаем настройки фильтров резюме
        settings = await self._resume_filter_settings_repository.get_by_resume_id(resume.id)
        if not settings:
            logger.warning(
                f"Для резюме {resume.id} не найдены настройки фильтров. "
                "Пропускаем обработку."
            )
            return

        # Проверяем обязательные поля настроек
        if not settings.text:
            logger.warning(
                f"Для резюме {resume.id} не заполнен text в настройках фильтров. "
                "Пропускаем обработку."
            )
            return

        if not settings.area:
            logger.warning(
                f"Для резюме {resume.id} не заполнен area в настройках фильтров. "
                "Пропускаем обработку."
            )
            return

        if settings.salary is None:
            logger.warning(
                f"Для резюме {resume.id} не заполнен salary в настройках фильтров. "
                "Пропускаем обработку."
            )
            return

        # 3. Получаем вакансии
        # Вычисляем количество страниц для получения нужного количества вакансий
        # Обычно на странице 20 вакансий, но может быть меньше
        # Запрашиваем больше страниц, чтобы гарантированно получить max_vacancies_per_resume
        pages_needed = (self._max_vacancies_per_resume // 20) + 2  # +2 для запаса
        page_indices = list(range(pages_needed))

        search_session_id = str(uuid.uuid4())

        # Создаем use case для обновления cookies
        update_cookies_uc = UpdateUserHhAuthCookiesUseCase(
            self._user_hh_auth_data_repository
        )

        try:
            vacancies = await self._search_and_get_filtered_vacancy_list_uc.execute(
                user_resume=resume.content,
                headers=auth_data.headers,
                cookies=auth_data.cookies,
                settings=settings,
                page_indices=page_indices,
                search_session_id=search_session_id,
                resume_id=resume.id,
                resume_hash=resume.headhunter_hash,
                user_filter_params=resume.user_parameters,
                user_id=resume.user_id,
                update_cookies_uc=update_cookies_uc,
            )
        except Exception as exc:
            logger.error(
                f"Ошибка при получении вакансий для резюме {resume.id}: {exc}",
                exc_info=True,
            )
            return

        # 4. Фильтруем вакансии: с confidence >= 0.5 (50%)
        suitable_vacancies = [
            v for v in vacancies 
            if (v.confidence or 0.0) >= 0.5
        ]

        # Ограничиваем количество вакансий
        if len(suitable_vacancies) > self._max_vacancies_per_resume:
            suitable_vacancies = suitable_vacancies[: self._max_vacancies_per_resume]

        # 5. Сортируем по confidence (сначала самые подходящие)
        suitable_vacancies.sort(key=lambda x: x.confidence or 0.0, reverse=True)

        logger.info(
            f"Для резюме {resume.id} найдено {len(suitable_vacancies)} подходящих вакансий "
            f"(confidence >= 50%, из {len(vacancies)} всего)"
        )

        # 6. Проверяем наличие headhunter_hash
        if not resume.headhunter_hash:
            logger.warning(
                f"Для резюме {resume.id} не указан headhunter_hash. "
                "Пропускаем отправку откликов."
            )
            return

        # 6.1. Проверяем актуальное состояние автоотклика перед началом откликов
        current_resume = await self._resume_repository.get_by_headhunter_hash(
            user_id=resume.user_id,
            headhunter_hash=resume.headhunter_hash,
        )
        if not current_resume:
            logger.warning(
                f"Резюме с headhunter_hash {resume.headhunter_hash} для пользователя "
                f"{resume.user_id} не найдено. Пропускаем отправку откликов."
            )
            return

        if not current_resume.is_auto_reply:
            logger.info(
                f"Автоотклик для резюме {current_resume.id} (headhunter_hash: {resume.headhunter_hash}) "
                f"выключен. Вакансии найдены ({len(suitable_vacancies)}), но отклики не отправляются."
            )
            return

        # 7. Обрабатываем каждую вакансию (каждый отклик в отдельной транзакции)
        for vacancy in suitable_vacancies:
            try:
                # Проверяем лимит перед каждым откликом
                if self._check_subscription_uc is not None:
                    try:
                        user_subscription, plan = await self._check_subscription_uc.execute(
                            resume.user_id
                        )
                        if user_subscription.responses_count >= plan.response_limit:
                            logger.info(
                                f"Лимит откликов для пользователя {resume.user_id} исчерпан: "
                                f"{user_subscription.responses_count}/{plan.response_limit}. "
                                f"Прекращаем обработку резюме {resume.id}"
                            )
                            raise SubscriptionLimitExceededError(
                                count=user_subscription.responses_count,
                                limit=plan.response_limit,
                            )
                    except ValueError:
                        # Если подписка не найдена, продолжаем
                        pass

                # Запускаем обработку вакансии в асинхронной задаче
                task = asyncio.create_task(
                    self._process_vacancy(
                        vacancy=vacancy,
                        resume=resume,
                        auth_data=auth_data,
                    )
                )
                
                # Обрабатываем ошибки в фоновой задаче
                def handle_task_result(task: asyncio.Task) -> None:
                    try:
                        task.result()
                    except AutoReplyDisabledError:
                        logger.info(
                            f"Обработка вакансий для резюме {resume.id} прекращена: автоотклик выключен"
                        )
                    except SubscriptionLimitExceededError as exc:
                        logger.info(
                            f"Обработка вакансий для резюме {resume.id} прекращена: "
                            f"лимит откликов исчерпан ({exc.count}/{exc.limit})"
                        )
                    except Exception as exc:
                        logger.error(
                            f"Ошибка при обработке вакансии {vacancy.vacancy_id} "
                            f"для резюме {resume.id}: {exc}",
                            exc_info=True,
                        )
                
                task.add_done_callback(handle_task_result)
            except Exception as exc:
                logger.error(
                    f"Ошибка при создании задачи для вакансии {vacancy.vacancy_id} "
                    f"для резюме {resume.id}: {exc}",
                    exc_info=True,
                )
                # Продолжаем обработку других вакансий

            # Пауза между откликами
            await asyncio.sleep(self._delay_between_replies_seconds)

    async def _process_vacancy(
        self,
        vacancy: FilteredVacancyListItem,
        resume: Resume,
        auth_data: UserHhAuthData,
    ) -> None:
        """Обработать одну вакансию: сгенерировать письмо и откликнуться.

        Args:
            vacancy: Вакансия для обработки (FilteredVacancyListItem).
            resume: Резюме кандидата.
            auth_data: Auth данные пользователя.
        """
        # Проверяем актуальное состояние автоотклика перед каждым откликом
        if not resume.headhunter_hash:
            logger.warning(
                f"Для резюме {resume.id} не указан headhunter_hash. "
                f"Пропускаем отклик на вакансию {vacancy.vacancy_id}."
            )
            return

        current_resume = await self._resume_repository.get_by_headhunter_hash(
            user_id=resume.user_id,
            headhunter_hash=resume.headhunter_hash,
        )
        if not current_resume:
            logger.warning(
                f"Резюме с headhunter_hash {resume.headhunter_hash} для пользователя "
                f"{resume.user_id} не найдено. Пропускаем отклик на вакансию {vacancy.vacancy_id}."
            )
            return

        if not current_resume.is_auto_reply:
            logger.info(
                f"Автоотклик для резюме {current_resume.id} (headhunter_hash: {resume.headhunter_hash}) "
                f"выключен. Прекращаем обработку вакансий."
            )
            raise AutoReplyDisabledError("Автоотклик выключен")

        # Формируем описание вакансии для генератора писем
        vacancy_description_parts = [f"Название: {vacancy.name}"]
        if vacancy.company_name:
            vacancy_description_parts.append(f"Компания: {vacancy.company_name}")
        if vacancy.area_name:
            vacancy_description_parts.append(f"Город: {vacancy.area_name}")
        if vacancy.snippet_requirement:
            vacancy_description_parts.append(f"Требования: {vacancy.snippet_requirement}")
        if vacancy.snippet_responsibility:
            vacancy_description_parts.append(
                f"Обязанности: {vacancy.snippet_responsibility}"
            )
        if vacancy.schedule_name:
            vacancy_description_parts.append(f"График: {vacancy.schedule_name}")

        vacancy_description = "\n".join(vacancy_description_parts)

        # Генерируем сопроводительное письмо
        try:
            cover_letter = await self._cover_letter_generator.generate(
                resume=resume.content,
                vacancy_description=vacancy_description,
                user_params=resume.user_parameters,
            )
        except Exception as exc:
            logger.error(
                f"Ошибка при генерации письма для вакансии {vacancy.vacancy_id}: {exc}",
                exc_info=True,
            )
            # Используем дефолтное письмо
            cover_letter = "1"

        if not cover_letter:
            cover_letter = "1"

        # Обрабатываем тест вакансии, если он есть
        test_answers: Dict[str, str | List[str]] | None = None
        test_metadata: Dict[str, str] | None = None
        internal_api_base_url = "https://krasnoyarsk.hh.ru"
        
        if vacancy.has_test:
            try:
                # Получаем тест вакансии
                get_vacancy_test_uc = GetVacancyTestUseCase(self._hh_client)
                test = await get_vacancy_test_uc.execute(
                    vacancy_id=vacancy.vacancy_id,
                    headers=auth_data.headers,
                    cookies=auth_data.cookies,
                    internal_api_base_url=internal_api_base_url,
                )
                
                if test is None:
                    logger.warning(
                        f"Тест для вакансии {vacancy.vacancy_id} не найден "
                        f"(возможно, форма с тестом отсутствует в HTML-странице). "
                        "Пропускаем вакансию."
                    )
                    return
                
                # Генерируем ответы на тест
                test_answers = await self._generate_test_answers_uc.execute(
                    test=test,
                    resume=resume.content,
                    user_params=resume.user_parameters,
                )
                
                if not test_answers:
                    logger.warning(
                        f"Не удалось сгенерировать ответы на тест для вакансии {vacancy.vacancy_id}. "
                        "Пропускаем вакансию."
                    )
                    return
                
                # Подготавливаем метаданные теста
                test_metadata = {
                    "uidPk": test.uid_pk or "",
                    "guid": test.guid or "",
                    "startTime": test.start_time or "",
                    "testRequired": str(test.test_required).lower(),
                }
                
                logger.info(
                    f"Подготовлены ответы на тест для вакансии {vacancy.vacancy_id}: "
                    f"{len(test_answers)} ответов"
                )
            except Exception as exc:
                logger.error(
                    f"Ошибка при обработке теста для вакансии {vacancy.vacancy_id}: {exc}",
                    exc_info=True,
                )
                # Пропускаем вакансию при ошибке обработки теста
                return

        # Отправляем отклик и сохраняем в БД (в отдельной транзакции для каждого отклика)
        try:
            if not resume.headhunter_hash:
                logger.error(
                    f"Для резюме {resume.id} не указан headhunter_hash. "
                    f"Пропускаем отправку отклика на вакансию {vacancy.vacancy_id}"
                )
                return
            
            logger.info(
                f"Отправка отклика: vacancy_id={vacancy.vacancy_id}, "
                f"resume_id={resume.id}, resume_hash={resume.headhunter_hash}, "
                f"user_id={resume.user_id}, has_test={vacancy.has_test}"
            )
            
            # Создаем отдельную транзакцию для каждого отклика
            unit_of_work = self._create_unit_of_work_factory()
            updated_cookies_from_hh = None
            async with unit_of_work:
                from domain.use_cases.create_vacancy_response import CreateVacancyResponseUseCase
                from domain.use_cases.respond_to_vacancy_and_save import RespondToVacancyAndSaveUseCase
                
                # Создаем Use Case для сохранения откликов в БД
                create_vacancy_response_uc = CreateVacancyResponseUseCase(
                    vacancy_response_repository=unit_of_work.vacancy_response_repository,
                )

                # НЕ передаем update_cookies_uc в транзакцию - обновим cookies после коммита
                # Создаем use cases для проверки подписки и инкремента счетчика
                from domain.use_cases.check_and_update_subscription import (
                    CheckAndUpdateSubscriptionUseCase,
                )
                from domain.use_cases.increment_response_count import (
                    IncrementResponseCountUseCase,
                )
                
                check_subscription_uc = CheckAndUpdateSubscriptionUseCase(
                    user_subscription_repository=unit_of_work.user_subscription_repository,
                    subscription_plan_repository=unit_of_work.subscription_plan_repository,
                )
                increment_response_count_uc = IncrementResponseCountUseCase(
                    check_subscription_uc=check_subscription_uc,
                    user_subscription_repository=unit_of_work.user_subscription_repository,
                )
                
                # Создаем составной Use Case для отклика с сохранением
                respond_to_vacancy_and_save_uc = RespondToVacancyAndSaveUseCase(
                    respond_to_vacancy_uc=self._respond_to_vacancy_uc,
                    create_vacancy_response_uc=create_vacancy_response_uc,
                    check_subscription_uc=check_subscription_uc,
                    increment_response_count_uc=increment_response_count_uc,
                )
                
                # Отправляем отклик БЕЗ обновления cookies в транзакции
                await respond_to_vacancy_and_save_uc.execute(
                    vacancy_id=vacancy.vacancy_id,
                    resume_id=resume.id,
                    user_id=resume.user_id,
                    resume_hash=resume.headhunter_hash,
                    headers=auth_data.headers,
                    cookies=auth_data.cookies,
                    letter=cover_letter,
                    vacancy_name=vacancy.name,
                    vacancy_url=vacancy.alternate_url,
                    test_answers=test_answers,
                    test_metadata=test_metadata,
                    internal_api_base_url=internal_api_base_url,
                    update_cookies_uc=None,  # Не обновляем cookies в транзакции
                )
                # Транзакция автоматически коммитится при выходе из async with
            
            # Cookies не обновляются сразу после отклика, чтобы избежать deadlock
            # Они обновятся при следующем запросе к HH API через HHHttpClientWithCookieUpdate
            logger.info(
                f"Успешно отправлен и сохранен отклик на вакансию {vacancy.vacancy_id} "
                f"для резюме {resume.id} (транзакция закоммичена)"
            )
        except Exception as exc:
            logger.error(
                f"Ошибка при отправке отклика на вакансию {vacancy.vacancy_id}: {exc}",
                exc_info=True,
            )
            raise
