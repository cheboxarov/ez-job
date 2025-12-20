"""Use case для удаления резюме."""

from __future__ import annotations

from uuid import UUID

from domain.interfaces.resume_repository_port import ResumeRepositoryPort


class DeleteResumeUseCase:
    """Use case для удаления резюме с проверкой принадлежности."""

    def __init__(self, resume_repository: ResumeRepositoryPort) -> None:
        """Инициализация use case.

        Args:
            resume_repository: Репозиторий резюме.
        """
        self._resume_repository = resume_repository

    async def execute(self, *, resume_id: UUID, user_id: UUID) -> None:
        """Удалить резюме.

        Проверяет принадлежность резюме пользователю перед удалением.

        Args:
            resume_id: UUID резюме.
            user_id: UUID пользователя (для проверки принадлежности).

        Raises:
            PermissionError: Если резюме не принадлежит пользователю.
            ValueError: Если резюме не найдено.
        """
        # Проверяем принадлежность
        belongs = await self._resume_repository.belongs_to_user(resume_id, user_id)
        if not belongs:
            raise PermissionError(
                f"Резюме {resume_id} не принадлежит пользователю {user_id}"
            )

        # Проверяем существование резюме
        existing_resume = await self._resume_repository.get_by_id(resume_id)
        if existing_resume is None:
            raise ValueError(f"Резюме с ID {resume_id} не найдено")

        await self._resume_repository.delete(resume_id)
