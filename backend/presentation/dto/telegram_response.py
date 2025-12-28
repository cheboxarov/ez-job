"""DTO для ответов API Telegram."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from domain.entities.telegram_notification_settings import TelegramNotificationSettings


class TelegramNotificationSettingsResponse(BaseModel):
    """DTO для настроек Telegram уведомлений."""

    id: UUID = Field(..., description="UUID настроек")
    user_id: UUID = Field(..., description="UUID пользователя")
    telegram_chat_id: int | None = Field(None, description="ID чата в Telegram")
    telegram_username: str | None = Field(None, description="Username в Telegram")
    is_enabled: bool = Field(..., description="Уведомления включены")
    notify_call_request: bool = Field(..., description="Уведомлять о собеседованиях")
    notify_external_action: bool = Field(
        ..., description="Уведомлять о требуемых действиях"
    )
    notify_question_answered: bool = Field(
        ..., description="Уведомлять об ответах на вопросы"
    )
    notify_message_suggestion: bool = Field(
        ..., description="Уведомлять о предложенных сообщениях"
    )
    notify_vacancy_response: bool = Field(
        ..., description="Уведомлять об отправленных откликах"
    )
    linked_at: datetime | None = Field(None, description="Дата привязки")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")

    @classmethod
    def from_entity(
        cls, settings: TelegramNotificationSettings
    ) -> "TelegramNotificationSettingsResponse":
        """Создает DTO из доменной сущности.

        Args:
            settings: Доменная сущность настроек Telegram.

        Returns:
            DTO для JSON ответа.
        """
        return cls(
            id=settings.id,
            user_id=settings.user_id,
            telegram_chat_id=settings.telegram_chat_id,
            telegram_username=settings.telegram_username,
            is_enabled=settings.is_enabled,
            notify_call_request=settings.notify_call_request,
            notify_external_action=settings.notify_external_action,
            notify_question_answered=settings.notify_question_answered,
            notify_message_suggestion=settings.notify_message_suggestion,
            notify_vacancy_response=settings.notify_vacancy_response,
            linked_at=settings.linked_at,
            created_at=settings.created_at,
            updated_at=settings.updated_at,
        )


class GenerateTelegramLinkTokenResponse(BaseModel):
    """DTO для ответа с токеном привязки Telegram."""

    link: str = Field(..., description="Ссылка для привязки аккаунта")
    expires_at: datetime = Field(..., description="Время истечения токена")


class SendTestNotificationResponse(BaseModel):
    """DTO для ответа на отправку тестового уведомления."""

    success: bool = Field(..., description="Успешность отправки")
