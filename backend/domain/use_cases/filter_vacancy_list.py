from __future__ import annotations

import asyncio
from typing import Dict, List

from domain.entities.filtered_vacancy_list import (
    FilteredVacancyListDto,
    FilteredVacancyListItem,
)
from domain.entities.vacancy_list import VacancyListItem
from domain.interfaces.vacancy_list_filter_service_port import VacancyListFilterServicePort


class FilterVacancyListUseCase:
    """Use case батчевой нейронной фильтрации list-вакансий.

    Принимает список list-вакансий и резюме, бьёт вакансии на чанки по batch_size
    и для каждого чанка вызывает сервис нейронной фильтрации. Затем применяет
    минимальный порог confidence и возвращает список отфильтрованных list-вакансий
    (list_item + confidence).
    """

    def __init__(
        self,
        filter_service: VacancyListFilterServicePort,
        minimal_confidence: float,
        batch_size: int = 50,
    ) -> None:
        self._filter_service = filter_service
        self._minimal_confidence = minimal_confidence
        self._batch_size = batch_size

    async def execute(
        self,
        vacancies: List[VacancyListItem],
        resume: str,
        user_filter_params: str | None = None,
    ) -> List[FilteredVacancyListItem]:
        if not vacancies:
            return []

        # Индексируем list items по id для последующей сборки
        by_id: Dict[int, VacancyListItem] = {v.vacancy_id: v for v in vacancies}

        all_dtos: list[FilteredVacancyListDto] = []

        # Чанкуем по batch_size, чтобы не раздувать контекст модели
        chunks: list[List[VacancyListItem]] = [
            vacancies[i : i + self._batch_size]
            for i in range(0, len(vacancies), self._batch_size)
        ]

        # Кидаем запросы в нейронку по чанкам асинхронно
        tasks = [
            asyncio.create_task(
                self._filter_service.filter_vacancy_list(chunk, resume, user_filter_params)
            )
            for chunk in chunks
        ]
        results = await asyncio.gather(*tasks)

        for dtos in results:
            all_dtos.extend(dtos)

        # Применяем порог confidence и собираем итоговый список
        result: list[FilteredVacancyListItem] = []
        for dto in all_dtos:
            if dto.confidence < self._minimal_confidence:
                continue
            list_item = by_id.get(dto.vacancy_id)
            if list_item is None:
                continue

            result.append(
                FilteredVacancyListItem.from_list_item(
                    list_item, dto.confidence, dto.reason
                )
            )

        return result

