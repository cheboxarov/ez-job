"""Реализация репозитория оценки резюме."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.resume_evaluation import ResumeEvaluation
from domain.interfaces.resume_evaluation_repository_port import ResumeEvaluationRepositoryPort
from infrastructure.database.models.resume_evaluation_model import ResumeEvaluationModel


class ResumeEvaluationRepository(ResumeEvaluationRepositoryPort):
    """Реализация репозитория оценки резюме для SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория.

        Args:
            session: Async сессия SQLAlchemy.
        """
        self._session = session

    async def get_by_content_hash(self, resume_content_hash: str) -> ResumeEvaluation | None:
        """Получить оценку резюме по хешу содержимого.

        Args:
            resume_content_hash: SHA256 хеш содержимого резюме.

        Returns:
            Доменная сущность ResumeEvaluation или None, если не найдено.
        """
        stmt = select(ResumeEvaluationModel).where(
            ResumeEvaluationModel.resume_content_hash == resume_content_hash
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def create(self, evaluation: ResumeEvaluation) -> ResumeEvaluation:
        """Создать новую оценку резюме.

        Args:
            evaluation: Доменная сущность ResumeEvaluation для создания.

        Returns:
            Созданная доменная сущность ResumeEvaluation с заполненным id.
        """
        model = ResumeEvaluationModel(
            id=evaluation.id if evaluation.id else uuid4(),
            resume_content_hash=evaluation.resume_content_hash,
            evaluation_data=evaluation.evaluation_data,
            created_at=evaluation.created_at if evaluation.created_at else datetime.now(),
            updated_at=evaluation.updated_at if evaluation.updated_at else datetime.now(),
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    def _to_domain(self, model: ResumeEvaluationModel) -> ResumeEvaluation:
        """Преобразовать SQLAlchemy модель в доменную сущность.

        Args:
            model: SQLAlchemy модель ResumeEvaluationModel.

        Returns:
            Доменная сущность ResumeEvaluation.
        """
        return ResumeEvaluation(
            id=model.id,
            resume_content_hash=model.resume_content_hash,
            evaluation_data=model.evaluation_data,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
