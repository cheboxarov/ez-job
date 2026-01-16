from __future__ import annotations

from typing import Dict, List, Optional
from uuid import UUID

from domain.entities.filtered_vacancy_list import FilteredVacancyListItem
from domain.entities.resume_filter_settings import ResumeFilterSettings
from domain.use_cases.get_filtered_vacancy_list_with_cache import (
    GetFilteredVacancyListWithCacheUseCase,
)
from domain.use_cases.get_vacancy_list import GetVacancyListUseCase
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase


class GetFilteredVacancyListUseCase:
    """Верхнеуровневый use case получения отфильтрованных list-вакансий.

    1. Получает list-вакансии через GetVacancyListUseCase (один запрос к /vacancies).
    2. Передаёт их в GetFilteredVacancyListWithCacheUseCase вместе с резюме.
    3. Возвращает список отфильтрованных list-вакансий (list_item + confidence).
    """

    def __init__(
        self,
        get_vacancy_list_uc: GetVacancyListUseCase,
        filter_vacancy_list_with_cache_uc: GetFilteredVacancyListWithCacheUseCase,
    ) -> None:
        self._get_vacancy_list_uc = get_vacancy_list_uc
        self._filter_vacancy_list_with_cache_uc = filter_vacancy_list_with_cache_uc

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
        resume_hash: str | None = None,
        user_filter_params: str | None = None,
        order_by: str | None = None,
        user_id: Optional[UUID] = None,
        update_cookies_uc: Optional[UpdateUserHhAuthCookiesUseCase] = None,
    ) -> List[FilteredVacancyListItem]:
        # 1. Получаем list-вакансии через существующий use case
        vacancy_list = await self._get_vacancy_list_uc.execute(
            headers=headers,
            cookies=cookies,
            settings=settings,
            text=text,
            page=page,
            search_session_id=search_session_id,
            resume_hash=resume_hash,
            order_by=order_by,
        )

        # 2. Фильтруем их через use case с кэшированием
        filtered: List[FilteredVacancyListItem] = await self._filter_vacancy_list_with_cache_uc.execute(
            vacancies=vacancy_list.items,
            resume_id=resume_id,
            resume=user_resume,
            user_filter_params=user_filter_params,
            user_id=user_id,
        )

        return filtered

