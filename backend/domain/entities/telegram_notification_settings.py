"""Доменная сущность настроек Telegram уведомлений."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class TelegramNotificationSettings:
    """Настройки Telegram уведомлений для пользователя."""

    id: UUID
    """Уникальный идентификатор настроек."""

    user_id: UUID
    """ID пользователя."""

    telegram_chat_id: int | None
    """ID чата в Telegram (заполняется после привязки)."""

    telegram_username: str | None
    """Username пользователя в Telegram (для отображения)."""

    is_enabled: bool
    """Глобальный переключатель уведомлений."""

    notify_call_request: bool
    """Уведомлять о собеседованиях и созвонах."""

    notify_external_action: bool
    """Уведомлять о требуемых действиях (формы, анкеты)."""

    notify_question_answered: bool
    """Уведомлять об ответах на вопросы."""

    notify_message_suggestion: bool
    """Уведомлять о предложенных сообщениях для отправки."""

    notify_vacancy_response: bool
    """Уведомлять об отправленных откликах на вакансии."""

    linked_at: datetime | None
    """Дата и время привязки Telegram аккаунта."""

    created_at: datetime
    """Дата и время создания записи."""

    updated_at: datetime
    """Дата и время последнего обновления."""
