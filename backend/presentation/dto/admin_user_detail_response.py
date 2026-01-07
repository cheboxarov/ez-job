"""DTO для детальной информации о пользователе для админки."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from domain.entities.subscription_plan import SubscriptionPlan
from domain.entities.user import User
from domain.entities.user_subscription import UserSubscription
from presentation.dto.subscription_response import SubscriptionPlanResponse


class AdminUserFlagsUpdateRequest(BaseModel):
    """Запрос на обновление флагов пользователя."""

    is_active: bool | None = Field(
        None, description="Новый статус активности пользователя"
    )
    is_verified: bool | None = Field(
        None, description="Новый статус подтверждения пользователя"
    )


class AdminChangeUserPlanRequest(BaseModel):
    """Запрос на смену плана пользователя."""

    plan_name: str = Field(..., description="Название нового плана (FREE, PLAN_1, ...)")


class AdminUserSubscriptionShort(BaseModel):
    """Краткая информация о подписке пользователя для админки."""

    plan_id: UUID = Field(..., description="UUID текущего плана")
    plan_name: str = Field(..., description="Название текущего плана")

    @classmethod
    def from_entities(
        cls,
        user_subscription: UserSubscription,
        plan: SubscriptionPlan,
    ) -> "AdminUserSubscriptionShort":
        return cls(plan_id=plan.id, plan_name=plan.name)


class AdminUserDetailResponse(BaseModel):
    """Детальная информация о пользователе для админки."""

    id: UUID = Field(..., description="UUID пользователя")
    email: str | None = Field(None, description="Email пользователя")
    phone: str | None = Field(None, description="Телефон пользователя")
    is_active: bool = Field(..., description="Признак активного пользователя")
    is_superuser: bool = Field(..., description="Признак администратора")
    is_verified: bool = Field(..., description="Признак подтверждённого email")
    subscription: AdminUserSubscriptionShort | None = Field(
        None, description="Текущая подписка пользователя"
    )

    @classmethod
    def from_entities(
        cls,
        user: User,
        user_subscription: UserSubscription | None,
        plan: SubscriptionPlan | None,
    ) -> "AdminUserDetailResponse":
        subscription: AdminUserSubscriptionShort | None = None
        if user_subscription is not None and plan is not None:
            subscription = AdminUserSubscriptionShort.from_entities(
                user_subscription, plan
            )

        return cls(
            id=user.id,
            email=user.email,
            phone=user.phone,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            is_verified=user.is_verified,
            subscription=subscription,
        )

