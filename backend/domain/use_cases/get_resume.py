"""Use case для получения резюме."""

from __future__ import annotations

from uuid import UUID

from domain.entities.resume import Resume
from domain.interfaces.resume_repository_port import ResumeRepositoryPort


class GetResumeUseCase:
    """Use case для получения резюме по ID с проверкой принадлежности."""

    def __init__(self, resume_repository: ResumeRepositoryPort) -> None:
        """Инициализация use case.

        Args:
            resume_repository: Репозиторий резюме.
        """
        self._resume_repository = resume_repository

    async def execute(self, *, resume_id: UUID, user_id: UUID) -> Resume | None:
        """Получить резюме по ID.

        Проверяет принадлежность резюме пользователю перед возвратом.

        Args:
            resume_id: UUID резюме.
            user_id: UUID пользователя (для проверки принадлежности).

        Returns:
            Доменная сущность Resume или None, если не найдено.

        Raises:
            PermissionError: Если резюме не принадлежит пользователю.
        """
        resume = await self._resume_repository.get_by_id(resume_id)
        if resume is None:
            return None

        # Проверяем принадлежность
        belongs = await self._resume_repository.belongs_to_user(resume_id, user_id)
        if not belongs:
            raise PermissionError(
                f"Резюме {resume_id} не принадлежит пользователю {user_id}"
            )

        return resume
