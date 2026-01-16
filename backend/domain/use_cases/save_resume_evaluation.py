"""Use case для сохранения оценки резюме."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

from domain.entities.resume_evaluation import ResumeEvaluation
from domain.exceptions.repository_exceptions import DuplicateEntityError
from domain.interfaces.resume_evaluation_repository_port import (
    ResumeEvaluationRepositoryPort,
)


class SaveResumeEvaluationUseCase:
    """Use case для сохранения оценки резюме в БД."""

    def __init__(self, resume_evaluation_repository: ResumeEvaluationRepositoryPort) -> None:
        """Инициализация.

        Args:
            resume_evaluation_repository: Репозиторий оценок резюме.
        """
        self._resume_evaluation_repository = resume_evaluation_repository

    async def execute(
        self, resume_content_hash: str, evaluation_data: Dict[str, Any]
    ) -> ResumeEvaluation:
        """Сохранить оценку резюме в БД.

        Args:
            resume_content_hash: SHA256 хеш содержимого резюме.
            evaluation_data: Dict с результатом оценки (conf, remarks, summary).

        Returns:
            Созданная доменная сущность ResumeEvaluation.
        """
        now = datetime.now()
        evaluation = ResumeEvaluation(
            id=uuid4(),
            resume_content_hash=resume_content_hash,
            evaluation_data=evaluation_data,
            created_at=now,
            updated_at=now,
        )
        try:
            result = await self._resume_evaluation_repository.create(evaluation)
        except DuplicateEntityError:
            # Запись уже существует (race condition), получаем существующую
            result = await self._resume_evaluation_repository.get_by_content_hash(
                resume_content_hash
            )
            if result is None:
                # Это не должно произойти, но на всякий случай
                raise
        return result
