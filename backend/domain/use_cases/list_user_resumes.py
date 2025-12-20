"""Use case для получения списка резюме пользователя."""

from __future__ import annotations

from uuid import UUID

from domain.entities.resume import Resume
from domain.interfaces.resume_repository_port import ResumeRepositoryPort


class ListUserResumesUseCase:
    """Use case для получения списка резюме пользователя."""

    def __init__(self, resume_repository: ResumeRepositoryPort) -> None:
        """Инициализация use case.

        Args:
            resume_repository: Репозиторий резюме.
        """
        self._resume_repository = resume_repository

    async def execute(self, *, user_id: UUID) -> list[Resume]:
        """Получить список резюме пользователя.

        Args:
            user_id: UUID пользователя.

        Returns:
            Список доменных сущностей Resume.
        """
        return await self._resume_repository.list_by_user_id(user_id)
