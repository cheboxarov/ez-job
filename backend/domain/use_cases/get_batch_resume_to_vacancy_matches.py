"""Use case для батчевого получения мэтчей резюме-вакансия."""

from __future__ import annotations

from typing import Dict, List
from uuid import UUID

from domain.entities.resume_to_vacancy_match import ResumeToVacancyMatch
from domain.interfaces.resume_to_vacancy_match_repository_port import (
    ResumeToVacancyMatchRepositoryPort,
)


class GetBatchResumeToVacancyMatchesUseCase:
    """Use case для батчевого получения мэтчей резюме-вакансия из БД."""

    def __init__(
        self, repository: ResumeToVacancyMatchRepositoryPort
    ) -> None:
        """Инициализация use case.

        Args:
            repository: Репозиторий для работы с мэтчами.
        """
        self._repository = repository

    async def execute(
        self, resume_id: UUID, vacancy_hashes: List[str]
    ) -> Dict[str, ResumeToVacancyMatch]:
        """Получить мэтчи по resume_id и списку vacancy_hash.

        Args:
            resume_id: UUID резюме.
            vacancy_hashes: Список hash вакансий.

        Returns:
            Словарь vacancy_hash -> ResumeToVacancyMatch для найденных мэтчей.
        """
        return await self._repository.get_batch_by_resume_and_vacancy_hashes(
            resume_id, vacancy_hashes
        )
