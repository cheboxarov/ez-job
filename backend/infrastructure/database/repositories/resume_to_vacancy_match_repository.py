"""Реализация репозитория мэтчей резюме-вакансия."""

from __future__ import annotations

from typing import Dict, List, Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from domain.entities.resume_to_vacancy_match import ResumeToVacancyMatch
from domain.interfaces.resume_to_vacancy_match_repository_port import (
    ResumeToVacancyMatchRepositoryPort,
)
from infrastructure.database.models.resume_to_vacancy_match_model import (
    ResumeToVacancyMatchModel,
)
from infrastructure.database.repositories.base_repository import BaseRepository


class ResumeToVacancyMatchRepository(BaseRepository, ResumeToVacancyMatchRepositoryPort):
    """Реализация репозитория мэтчей резюме-вакансия для SQLAlchemy."""

    def __init__(
        self, 
        session_or_factory: Union[AsyncSession, async_sessionmaker[AsyncSession]]
    ) -> None:
        """Инициализация репозитория.

        Args:
            session_or_factory: Либо AsyncSession (для транзакционного режима),
                               либо async_sessionmaker (для standalone режима).
        """
        super().__init__(session_or_factory)

    async def get_by_resume_and_vacancy_hash(
        self, resume_id: UUID, vacancy_hash: str
    ) -> ResumeToVacancyMatch | None:
        """Получить мэтч по resume_id и vacancy_hash.

        Args:
            resume_id: UUID резюме.
            vacancy_hash: Hash вакансии.

        Returns:
            Доменная сущность ResumeToVacancyMatch или None, если мэтч не найден.
        """
        async with self._get_session() as session:
            stmt = (
                select(ResumeToVacancyMatchModel)
                .where(ResumeToVacancyMatchModel.resume_id == resume_id)
                .where(ResumeToVacancyMatchModel.vacancy_hash == vacancy_hash)
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._to_domain(model)

    async def get_batch_by_resume_and_vacancy_hashes(
        self, resume_id: UUID, vacancy_hashes: List[str]
    ) -> Dict[str, ResumeToVacancyMatch]:
        """Батчевое получение мэтчей по resume_id и списку vacancy_hash.

        Args:
            resume_id: UUID резюме.
            vacancy_hashes: Список hash вакансий.

        Returns:
            Словарь vacancy_hash -> ResumeToVacancyMatch для найденных мэтчей.
        """
        if not vacancy_hashes:
            return {}

        async with self._get_session() as session:
            stmt = (
                select(ResumeToVacancyMatchModel)
                .where(ResumeToVacancyMatchModel.resume_id == resume_id)
                .where(ResumeToVacancyMatchModel.vacancy_hash.in_(vacancy_hashes))
            )
            result = await session.execute(stmt)
            models = result.scalars().all()

            return {
                model.vacancy_hash: self._to_domain(model) for model in models
            }

    async def create(self, match: ResumeToVacancyMatch) -> ResumeToVacancyMatch:
        """Создать новый мэтч.

        Args:
            match: Доменная сущность ResumeToVacancyMatch для создания.

        Returns:
            Созданная доменная сущность ResumeToVacancyMatch.
        """
        async with self._get_session() as session:
            from uuid import uuid4

            model = ResumeToVacancyMatchModel(
                id=uuid4(),
                resume_id=match.resume_id,
                vacancy_hash=match.vacancy_hash,
                confidence=match.confidence,
                reason=match.reason,
            )
            session.add(model)
            await session.flush()
            await session.refresh(model)
            return self._to_domain(model)

    async def create_batch(
        self, matches: List[ResumeToVacancyMatch]
    ) -> List[ResumeToVacancyMatch]:
        """Батчевое создание мэтчей.

        Args:
            matches: Список доменных сущностей ResumeToVacancyMatch для создания.

        Returns:
            Список созданных доменных сущностей ResumeToVacancyMatch.
        """
        if not matches:
            return []

        async with self._get_session() as session:
            from uuid import uuid4

            models = [
                ResumeToVacancyMatchModel(
                    id=uuid4(),
                    resume_id=match.resume_id,
                    vacancy_hash=match.vacancy_hash,
                    confidence=match.confidence,
                    reason=match.reason,
                )
                for match in matches
            ]
            session.add_all(models)
            await session.flush()
            for model in models:
                await session.refresh(model)
            return [self._to_domain(model) for model in models]

    def _to_domain(self, model: ResumeToVacancyMatchModel) -> ResumeToVacancyMatch:
        """Преобразовать SQLAlchemy модель в доменную сущность.

        Args:
            model: SQLAlchemy модель ResumeToVacancyMatchModel.

        Returns:
            Доменная сущность ResumeToVacancyMatch.
        """
        return ResumeToVacancyMatch(
            resume_id=model.resume_id,
            vacancy_hash=model.vacancy_hash,
            confidence=model.confidence,
            reason=model.reason,
        )
