from __future__ import annotations

from typing import Dict, List, Optional
from uuid import UUID

from domain.entities.resume_filter_settings import ResumeFilterSettings
from domain.entities.filtered_vacancy import FilteredVacancyDetail
from domain.entities.vacancy_detail import VacancyDetail
from domain.use_cases.fetch_vacancies import FetchVacanciesUseCase
from domain.use_cases.get_filtered_vacancies_with_cache import (
    GetFilteredVacanciesWithCacheUseCase,
)
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase


class GetFilteredVacanciesUseCase:
    """Верхнеуровневый use case получения отфильтрованных вакансий.

    1. Получает детальные вакансии через FetchVacanciesUseCase.
    2. Передаёт их в GetFilteredVacanciesWithCacheUseCase вместе с резюме.
    3. Возвращает список отфильтрованных вакансий (деталь + confidence).
"""

    def __init__(
        self,
        fetch_vacancies_uc: FetchVacanciesUseCase,
        filter_vacancies_with_cache_uc: GetFilteredVacanciesWithCacheUseCase,
    ) -> None:
        self._fetch_vacancies_uc = fetch_vacancies_uc
        self._filter_vacancies_with_cache_uc = filter_vacancies_with_cache_uc

    async def execute(
        self,
        *,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        settings: ResumeFilterSettings,
        text: str,
        page: str,
        search_session_id: str,
        user_resume: str,
        resume_id: UUID,
        user_filter_params: str | None = None,
        order_by: str | None = None,
        user_id: Optional[UUID] = None,
        update_cookies_uc: Optional[UpdateUserHhAuthCookiesUseCase] = None,
    ) -> List[FilteredVacancyDetail]:
        # 1. Получаем детальные вакансии через существующий use case
        details: List[VacancyDetail] = await self._fetch_vacancies_uc.execute(
            headers=headers,
            cookies=cookies,
            settings=settings,
            text=text,
            page=page,
            search_session_id=search_session_id,
            order_by=order_by,
            user_id=user_id,
            update_cookies_uc=update_cookies_uc,
        )

        # 2. Фильтруем их через use case с кэшированием
        filtered: List[FilteredVacancyDetail] = await self._filter_vacancies_with_cache_uc.execute(
            vacancies=details,
            resume_id=resume_id,
            resume=user_resume,
            user_filter_params=user_filter_params,
            user_id=user_id,
        )

        return filtered
