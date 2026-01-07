"""Сервис приложения для админских операций с тарифными планами."""

from __future__ import annotations

from typing import Sequence, Tuple
from uuid import UUID

from domain.entities.subscription_plan import SubscriptionPlan
from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from domain.use_cases.admin.list_subscription_plans_for_admin import (
    ListSubscriptionPlansForAdminUseCase,
)
from domain.use_cases.admin.upsert_subscription_plan import UpsertSubscriptionPlanUseCase


class AdminPlanService:
    """Сервис, оркестрирующий админские use case-ы по тарифным планам."""

    def __init__(self, unit_of_work: UnitOfWorkPort) -> None:
        self._unit_of_work = unit_of_work

    async def list_plans(
        self,
        page: int,
        page_size: int,
    ) -> Tuple[Sequence[SubscriptionPlan], int]:
        """Получить список тарифных планов для админки с пагинацией."""
        async with self._unit_of_work:
            use_case = ListSubscriptionPlansForAdminUseCase(
                subscription_plan_repository=self._unit_of_work.subscription_plan_repository,
            )
            return await use_case.execute(page=page, page_size=page_size)

    async def upsert_plan(
        self,
        *,
        plan_id: UUID | None,
        name: str,
        response_limit: int,
        reset_period_seconds: int,
        duration_days: int,
        price: float,
        is_active: bool,
    ) -> SubscriptionPlan:
        """Создать или обновить тарифный план."""
        async with self._unit_of_work:
            use_case = UpsertSubscriptionPlanUseCase(
                subscription_plan_repository=self._unit_of_work.subscription_plan_repository,
            )
            plan = await use_case.execute(
                plan_id=plan_id,
                name=name,
                response_limit=response_limit,
                reset_period_seconds=reset_period_seconds,
                duration_days=duration_days,
                price=price,
                is_active=is_active,
            )
            await self._unit_of_work.commit()
            return plan

    async def deactivate_plan(self, plan_id: UUID) -> SubscriptionPlan:
        """Деактивировать тарифный план."""
        async with self._unit_of_work:
            repo = self._unit_of_work.subscription_plan_repository
            plan = await repo.get_by_id(plan_id)
            if plan is None:
                raise ValueError(f"План подписки с ID {plan_id} не найден")
            plan.is_active = False
            plan = await repo.update(plan)
            await self._unit_of_work.commit()
            return plan

