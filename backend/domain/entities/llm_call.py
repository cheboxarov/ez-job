"""Доменная сущность для логирования вызовов LLM."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(slots=True)
class LlmCall:
    """Запись о вызове LLM.

    Содержит полную информацию о запросе к LLM, ответе, метриках и ошибках.
    """

    id: UUID
    """Уникальный идентификатор записи."""

    call_id: UUID
    """Идентификатор вызова (один для всех попыток одного вызова)."""

    attempt_number: int
    """Номер попытки (1, 2, 3...)."""

    agent_name: str
    """Имя агента (MessagesAgent, VacancyFilterAgent и т.д.)."""

    model: str
    """Модель LLM."""

    user_id: UUID | None
    """ID пользователя (опционально)."""

    prompt: list[dict[str, Any]]
    """Полный массив messages для промпта."""

    response: str
    """Полный текст ответа от LLM."""

    temperature: float
    """Температура модели."""

    response_format: dict[str, str] | None
    """Формат ответа (опционально)."""

    status: str
    """Статус: 'success' или 'error'."""

    error_type: str | None
    """Тип ошибки (класс исключения, опционально)."""

    error_message: str | None
    """Текст ошибки (опционально)."""

    duration_ms: int | None
    """Время выполнения в миллисекундах (опционально)."""

    prompt_tokens: int | None
    """Количество токенов в промпте (опционально)."""

    completion_tokens: int | None
    """Количество токенов в ответе (опционально)."""

    total_tokens: int | None
    """Общее количество токенов (опционально)."""

    response_size_bytes: int | None
    """Размер ответа в байтах (опционально)."""

    cost_usd: float | None
    """Стоимость вызова в USD (опционально)."""

    context: dict[str, Any] | None
    """Дополнительный контекст (use_case, resume_id, vacancy_id, chat_id и т.д.)."""

    created_at: datetime
    """Время создания записи."""
