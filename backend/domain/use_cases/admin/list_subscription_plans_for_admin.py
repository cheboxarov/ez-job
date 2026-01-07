from __future__ import annotations

from dataclasses import dataclass

from domain.entities.subscription_plan import SubscriptionPlan
from domain.interfaces.subscription_plan_repository_port import (
    SubscriptionPlanRepositoryPort,
)


@dataclass(slots=True)
class ListSubscriptionPlansForAdminUseCase:
    """Use case для получения списка тарифных планов для админки с пагинацией."""

    subscription_plan_repository: SubscriptionPlanRepositoryPort

    async def execute(
        self,
        page: int,
        page_size: int,
    ) -> tuple[list[SubscriptionPlan], int]:
        return await self.subscription_plan_repository.list_for_admin(
            page=page,
            page_size=page_size,
        )

