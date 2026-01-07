"""Реализация репозитория планов подписки."""

from __future__ import annotations

from typing import List, Tuple, Union
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from domain.entities.subscription_plan import SubscriptionPlan
from domain.interfaces.subscription_plan_repository_port import (
    SubscriptionPlanRepositoryPort,
)
from infrastructure.database.models.subscription_plan_model import SubscriptionPlanModel
from infrastructure.database.repositories.base_repository import BaseRepository


class SubscriptionPlanRepository(BaseRepository, SubscriptionPlanRepositoryPort):
    """Реализация репозитория планов подписки для SQLAlchemy."""

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

    async def get_by_id(self, plan_id: UUID) -> SubscriptionPlan | None:
        """Получить план подписки по ID.

        Args:
            plan_id: UUID плана подписки.

        Returns:
            Доменная сущность SubscriptionPlan или None, если не найдено.
        """
        async with self._get_session() as session:
            stmt = select(SubscriptionPlanModel).where(SubscriptionPlanModel.id == plan_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                return None
            return self._to_domain(model)

    async def get_by_name(self, name: str) -> SubscriptionPlan | None:
        """Получить план подписки по названию.

        Args:
            name: Название плана (FREE, PLAN_1, PLAN_2, PLAN_3).

        Returns:
            Доменная сущность SubscriptionPlan или None, если не найдено.
        """
        async with self._get_session() as session:
            stmt = select(SubscriptionPlanModel).where(SubscriptionPlanModel.name == name)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                return None
            return self._to_domain(model)

    async def get_all(self) -> List[SubscriptionPlan]:
        """Получить все активные планы подписки.

        Returns:
            Список доменных сущностей SubscriptionPlan.
        """
        async with self._get_session() as session:
            stmt = (
                select(SubscriptionPlanModel)
                .where(SubscriptionPlanModel.is_active == True)
                .order_by(SubscriptionPlanModel.price)
            )
            result = await session.execute(stmt)
            models = result.scalars().all()
            return [self._to_domain(model) for model in models]

    async def list_for_admin(
        self,
        page: int,
        page_size: int,
    ) -> Tuple[List[SubscriptionPlan], int]:
        """Получить планы для админки с пагинацией (все, включая неактивные)."""
        async with self._get_session() as session:
            stmt = select(SubscriptionPlanModel)

            count_stmt = stmt.with_only_columns(func.count()).order_by(None)
            total_result = await session.execute(count_stmt)
            total = int(total_result.scalar_one() or 0)

            offset = max(page - 1, 0) * page_size
            stmt = stmt.order_by(SubscriptionPlanModel.price).offset(offset).limit(
                page_size
            )

            result = await session.execute(stmt)
            models = result.scalars().all()
            return [self._to_domain(model) for model in models], total

    async def create(self, plan: SubscriptionPlan) -> SubscriptionPlan:
        async with self._get_session() as session:
            model = SubscriptionPlanModel(
                id=plan.id,
                name=plan.name,
                response_limit=plan.response_limit,
                reset_period_seconds=plan.reset_period_seconds,
                duration_days=plan.duration_days,
                price=plan.price,
                is_active=plan.is_active,
            )
            session.add(model)
            await session.flush()
            await session.refresh(model)
            return self._to_domain(model)

    async def update(self, plan: SubscriptionPlan) -> SubscriptionPlan:
        async with self._get_session() as session:
            stmt = select(SubscriptionPlanModel).where(SubscriptionPlanModel.id == plan.id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                raise ValueError(f"План подписки с ID {plan.id} не найден")

            model.name = plan.name
            model.response_limit = plan.response_limit
            model.reset_period_seconds = plan.reset_period_seconds
            model.duration_days = plan.duration_days
            model.price = plan.price
            model.is_active = plan.is_active

            await session.flush()
            await session.refresh(model)
            return self._to_domain(model)

    async def delete(self, plan_id: UUID) -> None:
        async with self._get_session() as session:
            stmt = select(SubscriptionPlanModel).where(SubscriptionPlanModel.id == plan_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                raise ValueError(f"План подписки с ID {plan_id} не найден")

            await session.delete(model)
            await session.flush()

    def _to_domain(self, model: SubscriptionPlanModel) -> SubscriptionPlan:
        """Преобразовать SQLAlchemy модель в доменную сущность.

        Args:
            model: SQLAlchemy модель SubscriptionPlanModel.

        Returns:
            Доменная сущность SubscriptionPlan.
        """
        return SubscriptionPlan(
            id=model.id,
            name=model.name,
            response_limit=model.response_limit,
            reset_period_seconds=model.reset_period_seconds,
            duration_days=model.duration_days,
            price=model.price,
            is_active=model.is_active,
        )
