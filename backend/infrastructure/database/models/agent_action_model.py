"""SQLAlchemy модель для действий агента."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from infrastructure.database.base import Base


class AgentActionModel(Base):
    """SQLAlchemy модель для хранения действий агентов.

    Хранит действия, созданные различными агентами (например, messages_agent).
    """

    __tablename__ = "agent_actions"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Тип действия (send_message, create_event и т.д.)",
    )
    entity_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Тип сущности (hh_dialog и т.д.)",
    )
    entity_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="ID сущности (например, ID диалога)",
    )
    created_by: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Идентификатор агента, создавшего действие",
    )
    data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="JSON данные действия (зависят от типа действия)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

