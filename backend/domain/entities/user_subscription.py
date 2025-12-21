"""Доменная сущность подписки пользователя."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass(slots=True)
class UserSubscription:
    """Доменная сущность подписки пользователя.

    Хранит текущее состояние подписки конкретного пользователя:
    - Текущий план подписки
    - Количество использованных откликов в текущем периоде
    - Время начала текущего периода сброса лимита
    - Срок действия подписки
    """

    user_id: UUID
    subscription_plan_id: UUID
    responses_count: int = 0
    period_started_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
