from __future__ import annotations

import asyncio
from typing import Dict, List, Optional
from uuid import UUID

from domain.entities.resume_filter_settings import ResumeFilterSettings
from domain.entities.filtered_vacancy import FilteredVacancyDetail
from domain.use_cases.get_filtered_vacancies import GetFilteredVacanciesUseCase
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase


class SearchAndGetFilteredVacanciesUseCase:
    """Верхнеуровневый use case для поиска и получения отфильтрованных вакансий.

    Объединяет логику:
    1. Генерации поисковой строки из резюме через GenerateSearchQueryUseCase
    2. Параллельной обработки нескольких страниц через GetFilteredVacanciesUseCase
    3. Объединения результатов всех страниц

    Выбрасывает ValueError, если не удалось сгенерировать поисковую строку.
    """

    def __init__(
        self,
        get_filtered_vacancies_uc: GetFilteredVacanciesUseCase,
    ) -> None:
        self._get_filtered_vacancies_uc = get_filtered_vacancies_uc

    async def execute(
        self,
        *,
        user_resume: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        settings: ResumeFilterSettings,
        page_indices: List[int],
        search_session_id: str,
        resume_id: UUID,
        user_filter_params: str | None = None,
        order_by: str | None = None,
        user_id: Optional[UUID] = None,
        update_cookies_uc: Optional[UpdateUserHhAuthCookiesUseCase] = None,
    ) -> List[FilteredVacancyDetail]:
        """Получает отфильтрованные вакансии с нескольких страниц, используя текст из настроек.

        Args:
            user_resume: Текст резюме кандидата.
            headers: HTTP заголовки для запросов к HH API.
            cookies: HTTP cookies для запросов к HH API.
            area: Код региона поиска.
            resume_id: ID резюме в HH.
            salary: Желаемая зарплата.
            page_indices: Список индексов страниц для обработки (например, [0, 1, 2]).
            search_session_id: ID сессии поиска.
            order_by: Опциональный параметр сортировки.
            user_filter_params: Дополнительные требования пользователя к фильтрации.

        Returns:
            Список отфильтрованных вакансий со всех обработанных страниц.

        Raises:
            ValueError: Если текст поиска не заполнен в настройках.
        """
        # 1. Берём поисковый текст из настроек фильтров резюме
        search_text = (settings.text or "").strip()
        if not search_text:
            raise ValueError("text не заполнен в настройках фильтров резюме")

        # 2. Создаем задачи для параллельной обработки страниц
        async def process_page(page_index: int) -> List[FilteredVacancyDetail]:
            page_str = str(page_index)
            return await self._get_filtered_vacancies_uc.execute(
                headers=headers,
                cookies=cookies,
                settings=settings,
                text=search_text,
                page=page_str,
                search_session_id=search_session_id,
                user_resume=user_resume,
                resume_id=resume_id,
                user_filter_params=user_filter_params,
                order_by=order_by,
                user_id=user_id,
                update_cookies_uc=update_cookies_uc,
            )

        # 3. Запускаем параллельную обработку всех страниц
        tasks = [asyncio.create_task(process_page(page)) for page in page_indices]
        results: List[List[FilteredVacancyDetail]] = await asyncio.gather(*tasks)

        # 4. Объединяем результаты всех страниц
        all_filtered: List[FilteredVacancyDetail] = []
        for page_results in results:
            all_filtered.extend(page_results)

        return all_filtered
