from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from domain.entities.subscription_plan import SubscriptionPlan
from domain.entities.user import User
from domain.entities.user_subscription import UserSubscription
from domain.interfaces.subscription_plan_repository_port import (
    SubscriptionPlanRepositoryPort,
)
from domain.interfaces.user_repository_port import UserRepositoryPort
from domain.interfaces.user_subscription_repository_port import (
    UserSubscriptionRepositoryPort,
)


@dataclass(slots=True)
class GetUserDetailForAdminUseCase:
    """Use case для получения детальной информации о пользователе для админки."""

    user_repository: UserRepositoryPort
    user_subscription_repository: UserSubscriptionRepositoryPort
    subscription_plan_repository: SubscriptionPlanRepositoryPort

    async def execute(
        self,
        user_id: UUID,
    ) -> tuple[User, UserSubscription | None, SubscriptionPlan | None]:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise ValueError(f"Пользователь с ID {user_id} не найден")

        user_subscription = await self.user_subscription_repository.get_by_user_id(
            user_id
        )
        plan: SubscriptionPlan | None = None

        if user_subscription is not None:
            plan = await self.subscription_plan_repository.get_by_id(
                user_subscription.subscription_plan_id
            )

        return user, user_subscription, plan

