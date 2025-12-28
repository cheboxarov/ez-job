"""DTO для запросов API Telegram."""

from __future__ import annotations

from pydantic import BaseModel, Field


class UpdateTelegramNotificationSettingsRequest(BaseModel):
    """DTO для обновления настроек Telegram уведомлений."""

    is_enabled: bool | None = Field(None, description="Включить/выключить уведомления")
    notify_call_request: bool | None = Field(
        None, description="Уведомлять о собеседованиях"
    )
    notify_external_action: bool | None = Field(
        None, description="Уведомлять о требуемых действиях"
    )
    notify_question_answered: bool | None = Field(
        None, description="Уведомлять об ответах на вопросы"
    )
    notify_message_suggestion: bool | None = Field(
        None, description="Уведомлять о предложенных сообщениях"
    )
    notify_vacancy_response: bool | None = Field(
        None, description="Уведомлять об отправленных откликах"
    )


class LinkTelegramAccountRequest(BaseModel):
    """DTO для привязки Telegram аккаунта."""

    token: str = Field(..., description="Токен привязки")
    telegram_chat_id: int = Field(..., description="ID чата в Telegram")
    telegram_username: str | None = Field(None, description="Username в Telegram")
