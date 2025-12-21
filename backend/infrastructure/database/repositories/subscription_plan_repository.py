"""Реализация репозитория планов подписки."""

from __future__ import annotations

from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.subscription_plan import SubscriptionPlan
from domain.interfaces.subscription_plan_repository_port import (
    SubscriptionPlanRepositoryPort,
)
from infrastructure.database.models.subscription_plan_model import SubscriptionPlanModel


class SubscriptionPlanRepository(SubscriptionPlanRepositoryPort):
    """Реализация репозитория планов подписки для SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория.

        Args:
            session: Async сессия SQLAlchemy.
        """
        self._session = session

    async def get_by_id(self, plan_id: UUID) -> SubscriptionPlan | None:
        """Получить план подписки по ID.

        Args:
            plan_id: UUID плана подписки.

        Returns:
            Доменная сущность SubscriptionPlan или None, если не найдено.
        """
        stmt = select(SubscriptionPlanModel).where(SubscriptionPlanModel.id == plan_id)
        result = await self._session.execute(stmt)
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
        stmt = select(SubscriptionPlanModel).where(SubscriptionPlanModel.name == name)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def get_all(self) -> List[SubscriptionPlan]:
        """Получить все активные планы подписки.

        Returns:
            Список доменных сущностей SubscriptionPlan.
        """
        stmt = (
            select(SubscriptionPlanModel)
            .where(SubscriptionPlanModel.is_active == True)
            .order_by(SubscriptionPlanModel.price)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

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
