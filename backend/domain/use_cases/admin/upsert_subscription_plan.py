from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID, uuid4

from domain.entities.subscription_plan import SubscriptionPlan
from domain.interfaces.subscription_plan_repository_port import (
    SubscriptionPlanRepositoryPort,
)


@dataclass(slots=True)
class UpsertSubscriptionPlanUseCase:
    """Use case для создания или обновления тарифного плана."""

    subscription_plan_repository: SubscriptionPlanRepositoryPort

    async def execute(
        self,
        *,
        plan_id: UUID | None,
        name: str,
        response_limit: int,
        reset_period_seconds: int,
        duration_days: int,
        price: Decimal,
        is_active: bool,
    ) -> SubscriptionPlan:
        if plan_id is not None:
            # Обновление существующего плана
            existing = await self.subscription_plan_repository.get_by_id(plan_id)
            if existing is None:
                raise ValueError(f"План подписки с ID {plan_id} не найден")

            existing.name = name
            existing.response_limit = response_limit
            existing.reset_period_seconds = reset_period_seconds
            existing.duration_days = duration_days
            existing.price = price
            existing.is_active = is_active

            return await self.subscription_plan_repository.update(existing)

        # Создание нового плана
        plan = SubscriptionPlan(
            id=uuid4(),
            name=name,
            response_limit=response_limit,
            reset_period_seconds=reset_period_seconds,
            duration_days=duration_days,
            price=price,
            is_active=is_active,
        )
        return await self.subscription_plan_repository.create(plan)

