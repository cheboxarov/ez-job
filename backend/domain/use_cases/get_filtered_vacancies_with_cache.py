"""Use case для получения отфильтрованных детальных вакансий с кэшированием."""

from __future__ import annotations

from typing import Callable, Dict, List
from uuid import UUID

from loguru import logger

from domain.entities.filtered_vacancy import FilteredVacancyDetail, FilteredVacancyDto
from domain.entities.resume_to_vacancy_match import ResumeToVacancyMatch
from domain.entities.vacancy_detail import VacancyDetail
from domain.exceptions.agent_exceptions import AgentParseError
from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from domain.interfaces.vacancy_filter_service_port import VacancyFilterServicePort
from domain.utils.vacancy_hash import calculate_vacancy_hash


class GetFilteredVacanciesWithCacheUseCase:
    """Use case для получения отфильтрованных детальных вакансий с кэшированием в БД.

    Сначала проверяет наличие мэтчей в БД, и только для отсутствующих
    отправляет запросы в нейронку. Сохраняет результаты нейронки в БД.
    """

    def __init__(
        self,
        create_unit_of_work: Callable[[], UnitOfWorkPort],
        filter_service: VacancyFilterServicePort,
        minimal_confidence: float,
        batch_size: int = 10,
    ) -> None:
        """Инициализация use case.

        Args:
            create_unit_of_work: Фабрика для создания UnitOfWork.
            filter_service: Сервис нейронной фильтрации.
            minimal_confidence: Минимальный порог confidence.
            batch_size: Размер батча для нейронной фильтрации.
        """
        self._create_uow = create_unit_of_work
        self._filter_service = filter_service
        self._minimal_confidence = minimal_confidence
        self._batch_size = batch_size

    async def execute(
        self,
        vacancies: List[VacancyDetail],
        resume_id: UUID,
        resume: str,
        user_filter_params: str | None = None,
        user_id: UUID | None = None,
    ) -> List[FilteredVacancyDetail]:
        """Получить отфильтрованные детальные вакансии с кэшированием.

        Args:
            vacancies: Список детальных вакансий для фильтрации.
            resume_id: UUID резюме.
            resume: Текст резюме кандидата.
            user_filter_params: Дополнительные требования пользователя к фильтрации.

        Returns:
            Список отфильтрованных детальных вакансий с confidence.
        """
        if not vacancies:
            return []

        # 1. Вычисляем vacancy_hash для каждой вакансии
        vacancy_hashes: Dict[int, str] = {
            v.vacancy_id: calculate_vacancy_hash(v.vacancy_id) for v in vacancies
        }
        vacancy_hash_list = list(vacancy_hashes.values())

        # 2. Получаем мэтчи из БД
        from domain.use_cases.get_batch_resume_to_vacancy_matches import (
            GetBatchResumeToVacancyMatchesUseCase,
        )

        async with self._create_uow() as uow:
            get_batch_matches_uc = GetBatchResumeToVacancyMatchesUseCase(
                uow.resume_to_vacancy_match_repository
            )
            found_matches = await get_batch_matches_uc.execute(
                resume_id, vacancy_hash_list
            )

        # 3. Разделяем вакансии на найденные и не найденные
        found_vacancy_ids: List[int] = []
        not_found_vacancies: List[VacancyDetail] = []
        found_matches_by_vacancy_id: Dict[int, ResumeToVacancyMatch] = {}

        for vacancy in vacancies:
            vacancy_hash = vacancy_hashes[vacancy.vacancy_id]
            match = found_matches.get(vacancy_hash)
            if match:
                found_vacancy_ids.append(vacancy.vacancy_id)
                found_matches_by_vacancy_id[vacancy.vacancy_id] = match
            else:
                not_found_vacancies.append(vacancy)

        # 4. Для вакансий без мэтчей вызываем нейронку
        new_matches: List[ResumeToVacancyMatch] = []
        if not_found_vacancies:
            # Чанкуем по batch_size
            chunks: List[List[VacancyDetail]] = [
                not_found_vacancies[i : i + self._batch_size]
                for i in range(0, len(not_found_vacancies), self._batch_size)
            ]

            import asyncio

            # Кидаем запросы в нейронку по чанкам асинхронно
            tasks = [
                self._filter_service.filter_vacancies(
                    chunk, resume, user_filter_params, user_id=user_id
                )
                for chunk in chunks
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Собираем результаты и создаем мэтчи
            for result in results:
                if isinstance(result, Exception):
                    if isinstance(result, AgentParseError):
                        logger.error(
                            f"Ошибка парсинга ответа агента при фильтрации вакансий: {result}",
                            exc_info=True,
                        )
                    else:
                        logger.error(
                            f"Ошибка при фильтрации вакансий: {result}",
                            exc_info=True,
                        )
                    continue
                
                dtos = result
                for dto in dtos:
                    vacancy_hash = vacancy_hashes[dto.vacancy_id]
                    match = ResumeToVacancyMatch(
                        resume_id=resume_id,
                        vacancy_hash=vacancy_hash,
                        confidence=dto.confidence,
                        reason=dto.reason,
                    )
                    new_matches.append(match)

            # 5. Сохраняем результаты нейронки в БД
            if new_matches:
                from domain.use_cases.create_batch_resume_to_vacancy_matches import (
                    CreateBatchResumeToVacancyMatchesUseCase,
                )
                async with self._create_uow() as uow:
                    create_batch_matches_uc = CreateBatchResumeToVacancyMatchesUseCase(
                        uow.resume_to_vacancy_match_repository
                    )
                    await create_batch_matches_uc.execute(new_matches)
                    await uow.commit()

        # 6. Объединяем результаты из БД и нейронки
        all_matches: Dict[int, ResumeToVacancyMatch] = found_matches_by_vacancy_id.copy()
        for match in new_matches:
            # Находим vacancy_id по vacancy_hash
            for vacancy_id, hash_val in vacancy_hashes.items():
                if hash_val == match.vacancy_hash:
                    all_matches[vacancy_id] = match
                    break

        # 7. Применяем минимальный порог confidence и собираем итоговый список
        result: List[FilteredVacancyDetail] = []
        by_id: Dict[int, VacancyDetail] = {v.vacancy_id: v for v in vacancies}

        for vacancy_id, match in all_matches.items():
            if match.confidence < self._minimal_confidence:
                continue
            detail = by_id.get(vacancy_id)
            if detail is None:
                continue

            result.append(
                FilteredVacancyDetail.from_detail(
                    detail, match.confidence, match.reason
                )
            )

        return result
