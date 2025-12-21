"""Доменная сущность плана подписки."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(slots=True)
class SubscriptionPlan:
    """Доменная сущность плана подписки.

    Справочник тарифов с лимитами откликов и периодами восстановления.
    """

    id: UUID
    name: str
    response_limit: int
    reset_period_seconds: int
    duration_days: int
    price: Decimal
    is_active: bool = True
