from __future__ import annotations

import asyncio
from typing import Dict, List, Optional
from uuid import UUID

from domain.entities.resume_filter_settings import ResumeFilterSettings
from domain.entities.filtered_vacancy import (
    FilteredVacancyDetail,
    FilteredVacancyDetailWithCoverLetter,
)
from domain.use_cases.generate_cover_letter import GenerateCoverLetterUseCase
from domain.use_cases.search_and_get_filtered_vacancies import (
    SearchAndGetFilteredVacanciesUseCase,
)
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase


class SearchAndGenerateCoverLettersUseCase:
    """Use case для поиска вакансий и генерации сопроводительных писем.

    Объединяет логику:
    1. Получения отфильтрованных вакансий через SearchAndGetFilteredVacanciesUseCase
    2. Фильтрации вакансий по confidence (порог min_confidence_for_cover_letter)
    3. Асинхронной генерации сопроводительных писем только для вакансий выше порога
    4. Возврата списка вакансий с опциональными письмами
    """

    def __init__(
        self,
        search_and_get_filtered_vacancies_uc: SearchAndGetFilteredVacanciesUseCase,
        generate_cover_letter_uc: GenerateCoverLetterUseCase,
    ) -> None:
        self._search_and_get_filtered_vacancies_uc = search_and_get_filtered_vacancies_uc
        self._generate_cover_letter_uc = generate_cover_letter_uc

    async def execute(
        self,
        *,
        user_resume: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        settings: ResumeFilterSettings,
        page_indices: List[int],
        search_session_id: str,
        user_filter_params: str | None = None,
        min_confidence_for_cover_letter: float,
        order_by: str | None = None,
        user_id: Optional[UUID] = None,
        update_cookies_uc: Optional[UpdateUserHhAuthCookiesUseCase] = None,
    ) -> List[FilteredVacancyDetailWithCoverLetter]:
        """Получает вакансии и генерирует сопроводительные письма для релевантных.

        Args:
            user_resume: Текст резюме кандидата.
            headers: HTTP заголовки для запросов к HH API.
            cookies: HTTP cookies для запросов к HH API.
            area: Код региона поиска.
            resume_id: ID резюме в HH.
            salary: Желаемая зарплата.
            page_indices: Список индексов страниц для обработки.
            search_session_id: ID сессии поиска.
            order_by: Опциональный параметр сортировки.
            user_filter_params: Дополнительные требования пользователя к фильтрации.
            min_confidence_for_cover_letter: Минимальный порог confidence для генерации письма.

        Returns:
            Список вакансий с опциональными сопроводительными письмами.
        """
        # 1. Получаем отфильтрованные вакансии
        filtered_vacancies: List[FilteredVacancyDetail] = (
            await self._search_and_get_filtered_vacancies_uc.execute(
                user_resume=user_resume,
                headers=headers,
                cookies=cookies,
                settings=settings,
                page_indices=page_indices,
                search_session_id=search_session_id,
                user_filter_params=user_filter_params,
                order_by=order_by,
                user_id=user_id,
                update_cookies_uc=update_cookies_uc,
            )
        )

        # 2. Разделяем вакансии на две группы по порогу confidence
        high_confidence: List[FilteredVacancyDetail] = []
        low_confidence: List[FilteredVacancyDetail] = []

        for vacancy in filtered_vacancies:
            confidence = vacancy.confidence or 0.0
            if confidence >= min_confidence_for_cover_letter:
                high_confidence.append(vacancy)
            else:
                low_confidence.append(vacancy)

        # 3. Асинхронно генерируем письма для вакансий выше порога
        async def generate_letter(
            vacancy: FilteredVacancyDetail,
        ) -> tuple[FilteredVacancyDetail, str | None]:
            """Генерирует письмо для вакансии, возвращает пару (вакансия, письмо)."""
            try:
                cover_letter = await self._generate_cover_letter_uc.execute(
                    vacancy=vacancy,
                    resume=user_resume,
                )
                return (vacancy, cover_letter if cover_letter else None)
            except Exception as exc:
                print(
                    f"[usecase] ошибка при генерации письма для вакансии {vacancy.vacancy_id}: {exc}",
                    flush=True,
                )
                return (vacancy, None)

        # Запускаем параллельную генерацию писем
        tasks = [asyncio.create_task(generate_letter(v)) for v in high_confidence]
        results: List[tuple[FilteredVacancyDetail, str | None]] = await asyncio.gather(*tasks)

        # 4. Создаем список результатов с письмами
        result: List[FilteredVacancyDetailWithCoverLetter] = []

        # Добавляем вакансии с письмами
        for vacancy, cover_letter in results:
            result.append(
                FilteredVacancyDetailWithCoverLetter.from_filtered_detail(
                    vacancy, cover_letter
                )
            )

        # Добавляем вакансии без писем (ниже порога)
        for vacancy in low_confidence:
            result.append(
                FilteredVacancyDetailWithCoverLetter.from_filtered_detail(vacancy, None)
            )

        return result
