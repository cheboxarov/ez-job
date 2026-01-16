"""DTO для запросов API настроек автоматизации."""

from __future__ import annotations

from pydantic import BaseModel, Field


class UpdateUserAutomationSettingsRequest(BaseModel):
    """DTO для обновления настроек автоматизации пользователя."""

    auto_reply_to_questions_in_chats: bool | None = Field(
        None, description="Автоматически отвечать на вопросы в чатах"
    )
    auto_watch_chats: bool | None = Field(
        None, description="Автоматически просматривать чаты агентом"
    )
