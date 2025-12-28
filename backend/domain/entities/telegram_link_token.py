"""Доменная сущность временного токена привязки Telegram."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class TelegramLinkToken:
    """Временный токен для привязки Telegram аккаунта."""

    id: UUID
    """Уникальный идентификатор токена."""

    user_id: UUID
    """ID пользователя, для которого создан токен."""

    token: str
    """Уникальный токен для deep link (формат: /start TOKEN)."""

    expires_at: datetime
    """Дата и время истечения токена."""

    created_at: datetime
    """Дата и время создания токена."""
