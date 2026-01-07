"""DTO для ответов API настроек автоматизации."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from domain.entities.user_automation_settings import UserAutomationSettings


class UserAutomationSettingsResponse(BaseModel):
    """DTO для настроек автоматизации пользователя."""

    id: UUID = Field(..., description="UUID настроек")
    user_id: UUID = Field(..., description="UUID пользователя")
    auto_reply_to_questions_in_chats: bool = Field(
        ..., description="Автоматически отвечать на вопросы в чатах"
    )
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")

    @classmethod
    def from_entity(
        cls, settings: UserAutomationSettings
    ) -> "UserAutomationSettingsResponse":
        """Создает DTO из доменной сущности.

        Args:
            settings: Доменная сущность настроек автоматизации.

        Returns:
            DTO для JSON ответа.
        """
        return cls(
            id=settings.id,
            user_id=settings.user_id,
            auto_reply_to_questions_in_chats=settings.auto_reply_to_questions_in_chats,
            created_at=settings.created_at,
            updated_at=settings.updated_at,
        )
