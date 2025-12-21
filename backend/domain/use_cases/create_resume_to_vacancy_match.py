"""Use case для создания мэтча резюме-вакансия."""

from __future__ import annotations

from domain.entities.resume_to_vacancy_match import ResumeToVacancyMatch
from domain.interfaces.resume_to_vacancy_match_repository_port import (
    ResumeToVacancyMatchRepositoryPort,
)


class CreateResumeToVacancyMatchUseCase:
    """Use case для создания мэтча резюме-вакансия в БД."""

    def __init__(
        self, repository: ResumeToVacancyMatchRepositoryPort
    ) -> None:
        """Инициализация use case.

        Args:
            repository: Репозиторий для работы с мэтчами.
        """
        self._repository = repository

    async def execute(self, match: ResumeToVacancyMatch) -> ResumeToVacancyMatch:
        """Создать мэтч в БД.

        Args:
            match: Доменная сущность ResumeToVacancyMatch для создания.

        Returns:
            Созданная доменная сущность ResumeToVacancyMatch.
        """
        return await self._repository.create(match)
