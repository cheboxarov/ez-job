from __future__ import annotations

import uuid
from typing import Dict, List, Optional
from uuid import UUID

from domain.entities.filtered_vacancy import FilteredVacancyDetailWithCoverLetter
from domain.entities.filtered_vacancy_list import FilteredVacancyListItem
from domain.entities.resume import Resume
from domain.entities.resume_filter_settings import ResumeFilterSettings
from domain.use_cases.respond_to_vacancy import RespondToVacancyUseCase
from domain.use_cases.respond_to_vacancy_and_save import RespondToVacancyAndSaveUseCase
from domain.use_cases.search_and_generate_cover_letters import (
    SearchAndGenerateCoverLettersUseCase,
)
from domain.use_cases.search_and_get_filtered_vacancy_list import (
    SearchAndGetFilteredVacancyListUseCase,
)
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase


class VacanciesService:
    """Сервис для получения релевантных вакансий через use case."""

    def __init__(
        self,
        search_and_generate_cover_letters_uc: SearchAndGenerateCoverLettersUseCase,
        search_and_get_filtered_vacancy_list_uc: SearchAndGetFilteredVacancyListUseCase | None = None,
        respond_to_vacancy_uc: RespondToVacancyUseCase | None = None,
        respond_to_vacancy_and_save_uc: RespondToVacancyAndSaveUseCase | None = None,
    ) -> None:
        self._use_case = search_and_generate_cover_letters_uc
        self._list_use_case = search_and_get_filtered_vacancy_list_uc
        self._respond_to_vacancy_uc = respond_to_vacancy_uc
        self._respond_to_vacancy_and_save_uc = respond_to_vacancy_and_save_uc

    async def get_relevant_vacancies_from_resume(
        self,
        *,
        resume: Resume,
        filter_settings: ResumeFilterSettings,
        page_indices: List[int],
        min_confidence_for_cover_letter: float,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        order_by: str | None = None,
        user_id: Optional[UUID] = None,
        update_cookies_uc: Optional[UpdateUserHhAuthCookiesUseCase] = None,
    ) -> List[FilteredVacancyDetailWithCoverLetter]:
        """Получает релевантные вакансии для резюме из БД.

        Данные резюме (content, user_parameters) берутся из доменной сущности Resume.
        Остальные параметры фильтрации (area, salary и др.) — из настроек фильтров пользователя.
        search_session_id генерируется автоматически.

        Args:
            resume: Доменная сущность резюме.
            filter_settings: Настройки фильтров пользователя.
            page_indices: Список индексов страниц для обработки.
            min_confidence_for_cover_letter: Минимальный порог confidence для генерации письма.
            order_by: Опциональный параметр сортировки.
            headers: HTTP заголовки для запросов к HH API.
            cookies: HTTP cookies для запросов к HH API.

        Returns:
            Отсортированный по убыванию confidence список вакансий.

        Raises:
            ValueError: Если обязательные поля резюме не заполнены.
            Exception: При ошибках выполнения use case.
        """
        # Валидация обязательных полей
        if not resume.content:
            raise ValueError("content не заполнен в резюме")

        # Генерация search_session_id
        search_session_id = str(uuid.uuid4())

        # Вызов внутреннего метода
        return await self._get_relevant_vacancies(
            user_resume=resume.content,
            filter_settings=filter_settings,
            user_filter_params=resume.user_parameters,
            search_session_id=search_session_id,
            page_indices=page_indices,
            min_confidence_for_cover_letter=min_confidence_for_cover_letter,
            order_by=order_by,
            headers=headers,
            cookies=cookies,
            user_id=user_id,
            resume_id=resume.id,  # Передаем resume_id для кэширования
            update_cookies_uc=update_cookies_uc,
        )

    async def _get_relevant_vacancies(
        self,
        *,
        user_resume: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        filter_settings: ResumeFilterSettings,
        page_indices: List[int],
        search_session_id: str,
        min_confidence_for_cover_letter: float,
        resume_id: UUID,
        user_filter_params: str | None = None,
        order_by: str | None = None,
        user_id: Optional[UUID] = None,
        update_cookies_uc: Optional[UpdateUserHhAuthCookiesUseCase] = None,
    ) -> List[FilteredVacancyDetailWithCoverLetter]:
        """Внутренний метод для получения релевантных вакансий и сортировки их по confidence.

        Args:
            user_resume: Текст резюме кандидата.
            headers: HTTP заголовки для запросов к HH API.
            cookies: HTTP cookies для запросов к HH API.
            area: Код региона поиска.
            resume_id: ID резюме в HH.
            salary: Желаемая зарплата.
            page_indices: Список индексов страниц для обработки.
            search_session_id: ID сессии поиска.
            min_confidence_for_cover_letter: Минимальный порог confidence для генерации письма.
            user_filter_params: Дополнительные требования пользователя к фильтрации.
            order_by: Опциональный параметр сортировки.

        Returns:
            Отсортированный по убыванию confidence список вакансий.

        Raises:
            ValueError: Если входные параметры некорректны.
            Exception: При ошибках выполнения use case.
        """
        try:
            vacancies = await self._use_case.execute(
                user_resume=user_resume,
                headers=headers,
                cookies=cookies,
                settings=filter_settings,
                page_indices=page_indices,
                search_session_id=search_session_id,
                resume_id=resume_id,
                min_confidence_for_cover_letter=min_confidence_for_cover_letter,
                user_filter_params=user_filter_params,
                order_by=order_by,
                user_id=user_id,
                update_cookies_uc=update_cookies_uc,
            )

            # Сортируем по убыванию confidence
            sorted_vacancies = sorted(
                vacancies, key=lambda v: v.confidence or 0.0, reverse=True
            )

            return sorted_vacancies
        except ValueError as exc:
            raise ValueError(f"Ошибка валидации: {exc}") from exc
        except Exception as exc:
            raise Exception(f"Ошибка при получении вакансий: {exc}") from exc

    async def get_relevant_vacancy_list_from_resume(
        self,
        *,
        resume: Resume,
        filter_settings: ResumeFilterSettings,
        page_indices: List[int],
        headers: Dict[str, str],
        cookies: Dict[str, str],
        order_by: str | None = None,
        user_id: Optional[UUID] = None,
        update_cookies_uc: Optional[UpdateUserHhAuthCookiesUseCase] = None,
    ) -> List[FilteredVacancyListItem]:
        resume_hash = resume.headhunter_hash
        """Получает релевантные list-вакансии для резюме из БД (без детальных запросов).

        Данные резюме (content, user_parameters) берутся из доменной сущности Resume.
        Остальные параметры фильтрации (area, salary и др.) — из настроек фильтров пользователя.
        search_session_id генерируется автоматически.

        Args:
            resume: Доменная сущность резюме.
            filter_settings: Настройки фильтров пользователя.
            page_indices: Список индексов страниц для обработки.
            order_by: Опциональный параметр сортировки.
            headers: HTTP заголовки для запросов к HH API.
            cookies: HTTP cookies для запросов к HH API.

        Returns:
            Отсортированный по убыванию confidence список list-вакансий.

        Raises:
            ValueError: Если обязательные поля резюме не заполнены или use case не настроен.
            Exception: При ошибках выполнения use case.
        """
        if self._list_use_case is None:
            raise ValueError("SearchAndGetFilteredVacancyListUseCase не настроен в сервисе")

        # Валидация обязательных полей
        if not resume.content:
            raise ValueError("content не заполнен в резюме")

        # Генерация search_session_id
        search_session_id = str(uuid.uuid4())

        try:
            vacancies = await self._list_use_case.execute(
                user_resume=resume.content,
                headers=headers,
                cookies=cookies,
                settings=filter_settings,
                page_indices=page_indices,
                search_session_id=search_session_id,
                resume_id=resume.id,
                resume_hash=resume_hash,
                user_filter_params=resume.user_parameters,
                order_by=order_by,
                user_id=user_id or resume.user_id,
                update_cookies_uc=update_cookies_uc,
            )

            # Сортируем по убыванию confidence
            sorted_vacancies = sorted(
                vacancies, key=lambda v: v.confidence or 0.0, reverse=True
            )

            return sorted_vacancies
        except ValueError as exc:
            raise ValueError(f"Ошибка валидации: {exc}") from exc
        except Exception as exc:
            raise Exception(f"Ошибка при получении list-вакансий: {exc}") from exc

    async def respond_to_vacancy(
        self,
        *,
        vacancy_id: int,
        resume_id: str,
        user_id: str,
        letter: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        resume_hash: str,
        vacancy_name: str | None = None,
        vacancy_url: str | None = None,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
    ) -> Dict[str, Any]:
        """Откликнуться на вакансию и сохранить в БД.

        Args:
            vacancy_id: ID вакансии в HeadHunter.
            resume_id: ID резюме в нашей БД (UUID).
            user_id: ID пользователя (UUID).
            letter: Текст сопроводительного письма.
            headers: HTTP заголовки для запросов к HH API.
            cookies: HTTP cookies для запросов к HH API.
            resume_hash: Hash резюме в HeadHunter (headhunter_hash).
            vacancy_name: Название вакансии (опционально, если не указано, будет использовано дефолтное).
            vacancy_url: URL вакансии (опционально).
            internal_api_base_url: Базовый URL внутреннего API HH.

        Returns:
            Ответ от API HH после отклика.

        Raises:
            ValueError: Если use case не настроен или обязательные поля не заполнены.
            Exception: При ошибках выполнения use case.
        """
        if self._respond_to_vacancy_and_save_uc is None:
            raise ValueError("RespondToVacancyAndSaveUseCase не настроен в сервисе")

        if not resume_hash:
            raise ValueError("headhunter_hash не заполнен в резюме")

        # Если название вакансии не указано, используем дефолтное
        if not vacancy_name:
            vacancy_name = f"Вакансия {vacancy_id}"

        from uuid import UUID
        try:
            result = await self._respond_to_vacancy_and_save_uc.execute(
                vacancy_id=vacancy_id,
                resume_id=UUID(resume_id),
                user_id=UUID(user_id),
                resume_hash=resume_hash,
                headers=headers,
                cookies=cookies,
                letter=letter,
                vacancy_name=vacancy_name,
                vacancy_url=vacancy_url,
                internal_api_base_url=internal_api_base_url,
            )
            return result
        except ValueError as exc:
            raise ValueError(f"Ошибка валидации: {exc}") from exc
        except Exception as exc:
            raise Exception(f"Ошибка при отклике на вакансию: {exc}") from exc

