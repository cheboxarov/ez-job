"""Use case для получения оценки резюме из кеша."""

from __future__ import annotations

from typing import Any, Dict

from domain.interfaces.resume_evaluation_repository_port import (
    ResumeEvaluationRepositoryPort,
)


class GetResumeEvaluationFromCacheUseCase:
    """Use case для получения оценки резюме из кеша по хешу содержимого."""

    def __init__(self, resume_evaluation_repository: ResumeEvaluationRepositoryPort) -> None:
        """Инициализация.

        Args:
            resume_evaluation_repository: Репозиторий оценок резюме.
        """
        self._resume_evaluation_repository = resume_evaluation_repository

    async def execute(self, resume_content_hash: str) -> Dict[str, Any] | None:
        """Получить оценку резюме из кеша.

        Args:
            resume_content_hash: SHA256 хеш содержимого резюме.

        Returns:
            Dict с оценкой (conf, remarks, summary) если найдено, иначе None.
        """
        evaluation = await self._resume_evaluation_repository.get_by_content_hash(
            resume_content_hash
        )

        if evaluation is None:
            return None

        return evaluation.evaluation_data
