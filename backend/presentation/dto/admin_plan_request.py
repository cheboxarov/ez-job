"""DTO для админских запросов по тарифным планам."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AdminPlanUpsertRequest(BaseModel):
    """Запрос на создание/обновление тарифного плана."""

    name: str = Field(..., description="Название плана")
    response_limit: int = Field(..., description="Лимит откликов за период")
    reset_period_seconds: int = Field(
        ..., description="Период сброса лимита в секундах"
    )
    duration_days: int = Field(
        ..., description="Срок действия подписки (0 = бессрочно)"
    )
    price: Decimal = Field(..., description="Цена плана")
    is_active: bool = Field(True, description="Активен ли план")


