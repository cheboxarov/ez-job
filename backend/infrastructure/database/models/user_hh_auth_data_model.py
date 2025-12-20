"""SQLAlchemy модель для HH auth data пользователя."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from infrastructure.database.base import Base


class UserHhAuthDataModel(Base):
    """SQLAlchemy модель для хранения HH headers/cookies пользователя.

    Связь 1:1 с пользователем (один пользователь = одна запись).
    """

    __tablename__ = "user_hh_auth_data"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    user_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    headers: Mapped[dict[str, str]] = mapped_column(
        JSONB,
        nullable=False,
        comment="HH API headers в формате JSON",
    )
    cookies: Mapped[dict[str, str]] = mapped_column(
        JSONB,
        nullable=False,
        comment="HH API cookies в формате JSON",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_user_hh_auth_data_user_id"),
    )
