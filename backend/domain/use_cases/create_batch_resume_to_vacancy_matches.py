"""Use case для батчевого создания мэтчей резюме-вакансия."""

from __future__ import annotations

from typing import List

from domain.entities.resume_to_vacancy_match import ResumeToVacancyMatch
from domain.interfaces.resume_to_vacancy_match_repository_port import (
    ResumeToVacancyMatchRepositoryPort,
)


class CreateBatchResumeToVacancyMatchesUseCase:
    """Use case для батчевого создания мэтчей резюме-вакансия в БД."""

    def __init__(
        self, repository: ResumeToVacancyMatchRepositoryPort
    ) -> None:
        """Инициализация use case.

        Args:
            repository: Репозиторий для работы с мэтчами.
        """
        self._repository = repository

    async def execute(
        self, matches: List[ResumeToVacancyMatch]
    ) -> List[ResumeToVacancyMatch]:
        """Создать мэтчи в БД батчем.

        Args:
            matches: Список доменных сущностей ResumeToVacancyMatch для создания.

        Returns:
            Список созданных доменных сущностей ResumeToVacancyMatch.
        """
        return await self._repository.create_batch(matches)
