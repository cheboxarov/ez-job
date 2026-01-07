"""SQLAlchemy модель для логирования вызовов LLM."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from infrastructure.database.base import Base


class LlmCallModel(Base):
    """SQLAlchemy модель для хранения логов вызовов LLM.

    Хранит полную информацию о каждом вызове LLM: промпт, ответ, метрики, ошибки.
    """

    __tablename__ = "llm_calls"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    call_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Идентификатор вызова (один для всех попыток одного вызова)",
    )
    attempt_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Номер попытки (1, 2, 3...)",
    )
    agent_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Имя агента (MessagesAgent, VacancyFilterAgent и т.д.)",
    )
    model: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Модель LLM",
    )
    user_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID пользователя",
    )
    prompt: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Полный массив messages для промпта",
    )
    response: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Полный текст ответа от LLM",
    )
    temperature: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Температура модели",
    )
    response_format: Mapped[dict[str, str] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Формат ответа (опционально)",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Статус: 'success' или 'error'",
    )
    error_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Тип ошибки (класс исключения)",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Текст ошибки",
    )
    duration_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Время выполнения в миллисекундах",
    )
    prompt_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Количество токенов в промпте",
    )
    completion_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Количество токенов в ответе",
    )
    total_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Общее количество токенов",
    )
    response_size_bytes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Размер ответа в байтах",
    )
    cost_usd: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Стоимость вызова в USD",
    )
    context: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Дополнительный контекст (use_case, resume_id, vacancy_id, chat_id и т.д.)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
