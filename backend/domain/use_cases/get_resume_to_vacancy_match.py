"""Use case для получения мэтча резюме-вакансия."""

from __future__ import annotations

from uuid import UUID

from domain.entities.resume_to_vacancy_match import ResumeToVacancyMatch
from domain.interfaces.resume_to_vacancy_match_repository_port import (
    ResumeToVacancyMatchRepositoryPort,
)


class GetResumeToVacancyMatchUseCase:
    """Use case для получения мэтча резюме-вакансия из БД."""

    def __init__(
        self, repository: ResumeToVacancyMatchRepositoryPort
    ) -> None:
        """Инициализация use case.

        Args:
            repository: Репозиторий для работы с мэтчами.
        """
        self._repository = repository

    async def execute(
        self, resume_id: UUID, vacancy_hash: str
    ) -> ResumeToVacancyMatch | None:
        """Получить мэтч по resume_id и vacancy_hash.

        Args:
            resume_id: UUID резюме.
            vacancy_hash: Hash вакансии.

        Returns:
            Доменная сущность ResumeToVacancyMatch или None, если мэтч не найден.
        """
        return await self._repository.get_by_resume_and_vacancy_hash(
            resume_id, vacancy_hash
        )
