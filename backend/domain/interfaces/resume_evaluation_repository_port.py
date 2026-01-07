"""Интерфейс репозитория для оценки резюме."""

from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities.resume_evaluation import ResumeEvaluation


class ResumeEvaluationRepositoryPort(ABC):
    """Порт репозитория для работы с оценками резюме."""

    @abstractmethod
    async def get_by_content_hash(self, resume_content_hash: str) -> ResumeEvaluation | None:
        """Получить оценку резюме по хешу содержимого.

        Args:
            resume_content_hash: SHA256 хеш содержимого резюме.

        Returns:
            Доменная сущность ResumeEvaluation или None, если не найдено.
        """
        pass

    @abstractmethod
    async def create(self, evaluation: ResumeEvaluation) -> ResumeEvaluation:
        """Создать новую оценку резюме.

        Args:
            evaluation: Доменная сущность ResumeEvaluation для создания.

        Returns:
            Созданная доменная сущность ResumeEvaluation с заполненным id.
        """
        pass
