"""DTO для ответов API подписок."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SubscriptionPlanResponse(BaseModel):
    """DTO для плана подписки."""

    id: UUID = Field(..., description="UUID плана")
    name: str = Field(..., description="Название плана")
    response_limit: int = Field(..., description="Лимит откликов за период")
    reset_period_seconds: int = Field(..., description="Период сброса лимита в секундах")
    duration_days: int = Field(..., description="Срок действия подписки (0 = бессрочно)")
    price: float = Field(..., description="Цена плана")


class UserSubscriptionResponse(BaseModel):
    """DTO для подписки пользователя."""

    plan_id: UUID = Field(..., description="UUID текущего плана")
    plan_name: str = Field(..., description="Название текущего плана")
    response_limit: int = Field(..., description="Лимит откликов плана")
    reset_period_seconds: int = Field(..., description="Период сброса лимита в секундах")
    responses_count: int = Field(..., description="Текущее количество откликов")
    period_started_at: Optional[datetime] = Field(
        None, description="Начало текущего периода сброса"
    )
    next_reset_at: Optional[datetime] = Field(
        None, description="Время следующего сброса лимита"
    )
    seconds_until_reset: Optional[int] = Field(
        None, description="Секунд до следующего сброса"
    )
    started_at: datetime = Field(..., description="Дата начала подписки")
    expires_at: Optional[datetime] = Field(
        None, description="Дата окончания подписки"
    )
    days_remaining: Optional[int] = Field(
        None, description="Дней до окончания подписки"
    )


class DailyResponsesResponse(BaseModel):
    """DTO для информации о лимитах откликов за день."""

    count: int = Field(..., description="Текущее количество откликов")
    limit: int = Field(..., description="Лимит откликов")
    remaining: int = Field(..., description="Осталось откликов")
    period_started_at: Optional[datetime] = Field(
        None, description="Начало текущего периода"
    )
    seconds_until_reset: Optional[int] = Field(
        None, description="Секунд до следующего сброса"
    )


class PlansListResponse(BaseModel):
    """DTO для списка планов подписки."""

    plans: list[SubscriptionPlanResponse] = Field(..., description="Список планов")
