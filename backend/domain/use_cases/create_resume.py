"""Use case для создания резюме."""

from __future__ import annotations

from uuid import UUID, uuid4

from domain.entities.resume import Resume
from domain.interfaces.resume_repository_port import ResumeRepositoryPort


class CreateResumeUseCase:
    """Use case для создания резюме."""

    def __init__(self, resume_repository: ResumeRepositoryPort) -> None:
        """Инициализация use case.

        Args:
            resume_repository: Репозиторий резюме.
        """
        self._resume_repository = resume_repository

    async def execute(
        self,
        *,
        user_id: UUID,
        content: str,
        user_parameters: str | None = None,
    ) -> Resume:
        """Создать резюме.

        Args:
            user_id: UUID пользователя.
            content: Текст резюме.
            user_parameters: Дополнительные параметры фильтрации.

        Returns:
            Созданная доменная сущность Resume.
        """
        resume = Resume(
            id=uuid4(),
            user_id=user_id,
            content=content,
            user_parameters=user_parameters,
        )
        return await self._resume_repository.create(resume)
