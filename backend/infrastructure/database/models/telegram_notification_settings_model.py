"""SQLAlchemy модель настроек Telegram уведомлений."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base import Base


class TelegramNotificationSettingsModel(Base):
    """SQLAlchemy модель настроек Telegram уведомлений."""

    __tablename__ = "telegram_notification_settings"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )
    user_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    telegram_chat_id: Mapped[int | None] = mapped_column(BigInteger(), nullable=True, unique=True)
    telegram_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean(), nullable=False, server_default="false")
    notify_call_request: Mapped[bool] = mapped_column(Boolean(), nullable=False, server_default="true")
    notify_external_action: Mapped[bool] = mapped_column(Boolean(), nullable=False, server_default="true")
    notify_question_answered: Mapped[bool] = mapped_column(Boolean(), nullable=False, server_default="true")
    notify_message_suggestion: Mapped[bool] = mapped_column(Boolean(), nullable=False, server_default="true")
    notify_vacancy_response: Mapped[bool] = mapped_column(Boolean(), nullable=False, server_default="true")
    linked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default="now()")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default="now()")
