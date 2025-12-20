"""Use case для обновления резюме."""

from __future__ import annotations

from uuid import UUID

from domain.entities.resume import Resume
from domain.interfaces.resume_repository_port import ResumeRepositoryPort


class UpdateResumeUseCase:
    """Use case для обновления резюме с проверкой принадлежности."""

    def __init__(self, resume_repository: ResumeRepositoryPort) -> None:
        """Инициализация use case.

        Args:
            resume_repository: Репозиторий резюме.
        """
        self._resume_repository = resume_repository

    async def execute(
        self,
        *,
        resume_id: UUID,
        user_id: UUID,
        content: str | None = None,
        user_parameters: str | None = None,
        is_auto_reply: bool | None = None,
    ) -> Resume:
        """Обновить резюме.

        Проверяет принадлежность резюме пользователю перед обновлением.

        Args:
            resume_id: UUID резюме.
            user_id: UUID пользователя (для проверки принадлежности).
            content: Новый текст резюме (опционально).
            user_parameters: Новые параметры фильтрации (опционально).
            is_auto_reply: Включен ли автоматический отклик (опционально).

        Returns:
            Обновленная доменная сущность Resume.

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

        # Получаем существующее резюме
        existing_resume = await self._resume_repository.get_by_id(resume_id)
        if existing_resume is None:
            raise ValueError(f"Резюме с ID {resume_id} не найдено")

        # Обновляем только переданные поля
        updated_resume = Resume(
            id=existing_resume.id,
            user_id=existing_resume.user_id,
            content=content if content is not None else existing_resume.content,
            user_parameters=(
                user_parameters
                if user_parameters is not None
                else existing_resume.user_parameters
            ),
            external_id=existing_resume.external_id,
            headhunter_hash=existing_resume.headhunter_hash,
            is_auto_reply=(
                is_auto_reply if is_auto_reply is not None else existing_resume.is_auto_reply
            ),
        )

        return await self._resume_repository.update(updated_resume)
