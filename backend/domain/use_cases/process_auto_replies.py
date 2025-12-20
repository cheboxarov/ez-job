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
from domain.interfaces.cover_letter_generator_port import CoverLetterGeneratorPort
from domain.interfaces.resume_filter_settings_repository_port import (
    ResumeFilterSettingsRepositoryPort,
)
from domain.interfaces.resume_repository_port import ResumeRepositoryPort
from domain.interfaces.user_hh_auth_data_repository_port import (
    UserHhAuthDataRepositoryPort,
)
from domain.use_cases.search_and_get_filtered_vacancy_list import (
    SearchAndGetFilteredVacancyListUseCase,
)


class AutoReplyDisabledError(Exception):
    """Исключение, которое бросается когда автоотклик выключен во время обработки."""


class ProcessAutoRepliesUseCase:
    """Use case для автоматической обработки откликов на вакансии.

    Для каждого резюме с включенным автооткликом:
    1. Получает подходящие вакансии (до 200 штук)
    2. Фильтрует вакансии без тестов (has_test == False)
    3. Сортирует по confidence (сначала самые подходящие)
    4. Для каждой вакансии генерирует письмо и отправляет отклик
    5. Делает паузу 30 секунд между откликами
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
        from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase
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

        # 4. Фильтруем вакансии: только без тестов
        suitable_vacancies = [v for v in vacancies if not v.has_test]

        # Ограничиваем количество вакансий
        if len(suitable_vacancies) > self._max_vacancies_per_resume:
            suitable_vacancies = suitable_vacancies[: self._max_vacancies_per_resume]

        # 5. Сортируем по confidence (сначала самые подходящие)
        suitable_vacancies.sort(key=lambda x: x.confidence or 0.0, reverse=True)

        logger.info(
            f"Для резюме {resume.id} найдено {len(suitable_vacancies)} подходящих вакансий "
            f"(без тестов, из {len(vacancies)} всего)"
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
                await self._process_vacancy(
                    vacancy=vacancy,
                    resume=resume,
                    auth_data=auth_data,
                )
            except AutoReplyDisabledError:
                # Автоотклик выключен во время обработки - прекращаем весь цикл
                logger.info(
                    f"Обработка вакансий для резюме {resume.id} прекращена: автоотклик выключен"
                )
                break
            except Exception as exc:
                logger.error(
                    f"Ошибка при обработке вакансии {vacancy.vacancy_id} "
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
                f"user_id={resume.user_id}"
            )
            
            # Создаем отдельную транзакцию для каждого отклика
            unit_of_work = self._create_unit_of_work_factory()
            async with unit_of_work:
                from domain.use_cases.create_vacancy_response import CreateVacancyResponseUseCase
                from domain.use_cases.respond_to_vacancy_and_save import RespondToVacancyAndSaveUseCase
                
                # Создаем Use Case для сохранения откликов в БД
                create_vacancy_response_uc = CreateVacancyResponseUseCase(
                    vacancy_response_repository=unit_of_work.vacancy_response_repository,
                )

                # Создаем use case для обновления cookies в этой транзакции
                update_cookies_uc_in_transaction = UpdateUserHhAuthCookiesUseCase(
                    unit_of_work.user_hh_auth_data_repository
                )

                # Создаем составной Use Case для отклика с сохранением
                respond_to_vacancy_and_save_uc = RespondToVacancyAndSaveUseCase(
                    respond_to_vacancy_uc=self._respond_to_vacancy_uc,
                    create_vacancy_response_uc=create_vacancy_response_uc,
                )
                
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
                    update_cookies_uc=update_cookies_uc_in_transaction,
                )
                # Транзакция автоматически коммитится при выходе из async with
            
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
