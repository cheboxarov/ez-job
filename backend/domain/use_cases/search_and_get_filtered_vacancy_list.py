from __future__ import annotations

import asyncio
from typing import Dict, List, Optional
from uuid import UUID

from domain.entities.filtered_vacancy_list import FilteredVacancyListItem
from domain.entities.resume_filter_settings import ResumeFilterSettings
from domain.use_cases.get_filtered_vacancy_list import GetFilteredVacancyListUseCase
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase


class SearchAndGetFilteredVacancyListUseCase:
    """Верхнеуровневый use case для поиска и получения отфильтрованных list-вакансий.

    Объединяет логику:
    1. Генерации поисковой строки из резюме через settings.text
    2. Параллельной обработки нескольких страниц через GetFilteredVacancyListUseCase
    3. Объединения результатов всех страниц

    Выбрасывает ValueError, если не удалось получить поисковую строку из настроек.
    """

    def __init__(
        self,
        get_filtered_vacancy_list_uc: GetFilteredVacancyListUseCase,
    ) -> None:
        self._get_filtered_vacancy_list_uc = get_filtered_vacancy_list_uc

    async def execute(
        self,
        *,
        user_resume: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        settings: ResumeFilterSettings,
        page_indices: List[int],
        search_session_id: str,
        resume_hash: str | None = None,
        user_filter_params: str | None = None,
        order_by: str | None = None,
        user_id: Optional[UUID] = None,
        update_cookies_uc: Optional[UpdateUserHhAuthCookiesUseCase] = None,
    ) -> List[FilteredVacancyListItem]:
        """Получает отфильтрованные list-вакансии с нескольких страниц, используя текст из настроек.

        Args:
            user_resume: Текст резюме кандидата.
            headers: HTTP заголовки для запросов к HH API.
            cookies: HTTP cookies для запросов к HH API.
            settings: Настройки фильтров резюме (включая text для поиска).
            page_indices: Список индексов страниц для обработки (например, [0, 1, 2]).
            search_session_id: ID сессии поиска.
            order_by: Опциональный параметр сортировки.
            user_filter_params: Дополнительные требования пользователя к фильтрации.

        Returns:
            Список отфильтрованных list-вакансий со всех обработанных страниц.

        Raises:
            ValueError: Если текст поиска не заполнен в настройках.
        """
        # 1. Берём поисковый текст из настроек фильтров резюме
        search_text = (settings.text or "").strip()
        if not search_text:
            raise ValueError("text не заполнен в настройках фильтров резюме")

        # 2. Создаем задачи для параллельной обработки страниц
        async def process_page(page_index: int) -> List[FilteredVacancyListItem]:
            page_str = str(page_index)
            return await self._get_filtered_vacancy_list_uc.execute(
                headers=headers,
                cookies=cookies,
                settings=settings,
                text=search_text,
                page=page_str,
                search_session_id=search_session_id,
                user_resume=user_resume,
                resume_hash=resume_hash,
                user_filter_params=user_filter_params,
                order_by=order_by,
                user_id=user_id,
                update_cookies_uc=update_cookies_uc,
            )

        # 3. Запускаем параллельную обработку всех страниц
        tasks = [asyncio.create_task(process_page(page)) for page in page_indices]
        results: List[List[FilteredVacancyListItem]] = await asyncio.gather(*tasks)

        # 4. Объединяем результаты всех страниц
        all_filtered: List[FilteredVacancyListItem] = []
        for page_results in results:
            all_filtered.extend(page_results)

        return all_filtered

