"""DTO для запросов API подписок."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChangePlanRequest(BaseModel):
    """DTO для запроса смены плана подписки."""

    plan_name: str = Field(..., description="Название плана (FREE, PLAN_1, PLAN_2, PLAN_3)")

