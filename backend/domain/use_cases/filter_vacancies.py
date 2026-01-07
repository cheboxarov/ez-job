from __future__ import annotations

import asyncio
from typing import Dict, List
from uuid import UUID

from domain.entities.filtered_vacancy import FilteredVacancyDetail, FilteredVacancyDto
from domain.entities.vacancy_detail import VacancyDetail
from domain.interfaces.vacancy_filter_service_port import VacancyFilterServicePort


class FilterVacanciesUseCase:
    """Use case батчевой нейронной фильтрации вакансий.

    Принимает список детальных вакансий и резюме, бьёт вакансии на чанки по 10
    и для каждого чанка вызывает сервис нейронной фильтрации. Затем применяет
    минимальный порог confidence и возвращает список отфильтрованных вакансий
    (деталь + confidence).
    """

    def __init__(
        self,
        filter_service: VacancyFilterServicePort,
        minimal_confidence: float,
        batch_size: int = 10,
    ) -> None:
        self._filter_service = filter_service
        self._minimal_confidence = minimal_confidence
        self._batch_size = batch_size

    async def execute(
        self,
        vacancies: List[VacancyDetail],
        resume: str,
        user_filter_params: str | None = None,
        user_id: UUID | None = None,
    ) -> List[FilteredVacancyDetail]:
        if not vacancies:
            return []

        # Индексируем детали по id для последующей сборки
        by_id: Dict[int, VacancyDetail] = {v.vacancy_id: v for v in vacancies}

        all_dtos: list[FilteredVacancyDto] = []

        # Чанкуем по batch_size, чтобы не раздувать контекст модели
        chunks: list[List[VacancyDetail]] = [
            vacancies[i : i + self._batch_size]
            for i in range(0, len(vacancies), self._batch_size)
        ]

        # Кидаем запросы в нейронку по чанкам асинхронно
        tasks = [
            asyncio.create_task(
                self._filter_service.filter_vacancies(chunk, resume, user_filter_params, user_id)
            )
            for chunk in chunks
        ]
        results = await asyncio.gather(*tasks)

        for dtos in results:
            all_dtos.extend(dtos)

        # Применяем порог confidence и собираем итоговый список
        result: list[FilteredVacancyDetail] = []
        for dto in all_dtos:
            if dto.confidence < self._minimal_confidence:
                continue
            detail = by_id.get(dto.vacancy_id)
            if detail is None:
                continue

            result.append(FilteredVacancyDetail.from_detail(detail, dto.confidence, dto.reason))

        return result
