"""Use case для получения отфильтрованных list-вакансий с кэшированием."""

from __future__ import annotations

from typing import Dict, List
from uuid import UUID

from domain.entities.filtered_vacancy_list import (
    FilteredVacancyListItem,
    FilteredVacancyListDto,
)
from domain.entities.resume_to_vacancy_match import ResumeToVacancyMatch
from domain.entities.vacancy_list import VacancyListItem
from domain.interfaces.vacancy_list_filter_service_port import (
    VacancyListFilterServicePort,
)
from domain.utils.vacancy_hash import calculate_vacancy_hash
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


class GetFilteredVacancyListWithCacheUseCase:
    """Use case для получения отфильтрованных list-вакансий с кэшированием в БД.

    Сначала проверяет наличие мэтчей в БД, и только для отсутствующих
    отправляет запросы в нейронку. Сохраняет результаты нейронки в БД.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        filter_service: VacancyListFilterServicePort,
        minimal_confidence: float,
        batch_size: int = 50,
    ) -> None:
        """Инициализация use case.

        Args:
            session_factory: Фабрика для создания async сессий SQLAlchemy.
            filter_service: Сервис нейронной фильтрации.
            minimal_confidence: Минимальный порог confidence.
            batch_size: Размер батча для нейронной фильтрации.
        """
        self._session_factory = session_factory
        self._filter_service = filter_service
        self._minimal_confidence = minimal_confidence
        self._batch_size = batch_size

    async def execute(
        self,
        vacancies: List[VacancyListItem],
        resume_id: UUID,
        resume: str,
        user_filter_params: str | None = None,
    ) -> List[FilteredVacancyListItem]:
        """Получить отфильтрованные list-вакансии с кэшированием.

        Args:
            vacancies: Список list-вакансий для фильтрации.
            resume_id: UUID резюме.
            resume: Текст резюме кандидата.
            user_filter_params: Дополнительные требования пользователя к фильтрации.

        Returns:
            Список отфильтрованных list-вакансий с confidence.
        """
        if not vacancies:
            return []

        # 1. Вычисляем vacancy_hash для каждой вакансии
        vacancy_hashes: Dict[int, str] = {
            v.vacancy_id: calculate_vacancy_hash(v.vacancy_id) for v in vacancies
        }
        vacancy_hash_list = list(vacancy_hashes.values())

        # 2. Получаем мэтчи из БД
        from infrastructure.database.repositories.resume_to_vacancy_match_repository import (
            ResumeToVacancyMatchRepository,
        )
        from domain.use_cases.get_batch_resume_to_vacancy_matches import (
            GetBatchResumeToVacancyMatchesUseCase,
        )
        
        async with self._session_factory() as session:
            match_repository = ResumeToVacancyMatchRepository(session)
            get_batch_matches_uc = GetBatchResumeToVacancyMatchesUseCase(match_repository)
            found_matches = await get_batch_matches_uc.execute(
                resume_id, vacancy_hash_list
            )

        # 3. Разделяем вакансии на найденные и не найденные
        found_vacancy_ids: List[int] = []
        not_found_vacancies: List[VacancyListItem] = []
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
            chunks: List[List[VacancyListItem]] = [
                not_found_vacancies[i : i + self._batch_size]
                for i in range(0, len(not_found_vacancies), self._batch_size)
            ]

            import asyncio

            # Кидаем запросы в нейронку по чанкам асинхронно
            tasks = [
                self._filter_service.filter_vacancy_list(
                    chunk, resume, user_filter_params
                )
                for chunk in chunks
            ]
            results = await asyncio.gather(*tasks)

            # Собираем результаты и создаем мэтчи
            for dtos in results:
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
                async with self._session_factory() as session:
                    match_repository = ResumeToVacancyMatchRepository(session)
                    create_batch_matches_uc = CreateBatchResumeToVacancyMatchesUseCase(match_repository)
                    await create_batch_matches_uc.execute(new_matches)
                    await session.commit()

        # 6. Объединяем результаты из БД и нейронки
        all_matches: Dict[int, ResumeToVacancyMatch] = found_matches_by_vacancy_id.copy()
        for match in new_matches:
            # Находим vacancy_id по vacancy_hash
            for vacancy_id, hash_val in vacancy_hashes.items():
                if hash_val == match.vacancy_hash:
                    all_matches[vacancy_id] = match
                    break

        # 7. Применяем минимальный порог confidence и собираем итоговый список
        result: List[FilteredVacancyListItem] = []
        by_id: Dict[int, VacancyListItem] = {v.vacancy_id: v for v in vacancies}

        for vacancy_id, match in all_matches.items():
            if match.confidence < self._minimal_confidence:
                continue
            list_item = by_id.get(vacancy_id)
            if list_item is None:
                continue

            result.append(
                FilteredVacancyListItem.from_list_item(
                    list_item, match.confidence, match.reason
                )
            )

        return result
