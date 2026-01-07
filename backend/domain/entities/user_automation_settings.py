"""Доменная сущность настроек автоматизации пользователя."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class UserAutomationSettings:
    """Настройки автоматизации для пользователя."""

    id: UUID
    """Уникальный идентификатор настроек."""

    user_id: UUID
    """ID пользователя."""

    auto_reply_to_questions_in_chats: bool
    """Автоматически отвечать на вопросы в чатах."""

    created_at: datetime
    """Дата и время создания записи."""

    updated_at: datetime
    """Дата и время последнего обновления."""
