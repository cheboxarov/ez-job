"""DTO для ответов админских LLM вызовов."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class LlmCallResponse(BaseModel):
    """DTO для вызова LLM."""

    id: UUID = Field(..., description="UUID записи")
    call_id: UUID = Field(..., description="UUID вызова")
    attempt_number: int = Field(..., description="Номер попытки")
    agent_name: str = Field(..., description="Имя агента")
    model: str = Field(..., description="Модель LLM")
    user_id: UUID | None = Field(None, description="ID пользователя")
    prompt: list[dict[str, Any]] = Field(..., description="Промпт (массив messages)")
    response: str = Field(..., description="Ответ LLM")
    temperature: float = Field(..., description="Температура модели")
    response_format: dict[str, str] | None = Field(None, description="Формат ответа")
    status: str = Field(..., description="Статус ('success' или 'error')")
    error_type: str | None = Field(None, description="Тип ошибки")
    error_message: str | None = Field(None, description="Текст ошибки")
    duration_ms: int | None = Field(None, description="Время выполнения в мс")
    prompt_tokens: int | None = Field(None, description="Токены в промпте")
    completion_tokens: int | None = Field(None, description="Токены в ответе")
    total_tokens: int | None = Field(None, description="Общее количество токенов")
    response_size_bytes: int | None = Field(None, description="Размер ответа в байтах")
    cost_usd: float | None = Field(None, description="Стоимость вызова в USD")
    context: dict[str, Any] | None = Field(None, description="Дополнительный контекст")
    created_at: datetime = Field(..., description="Время создания")

    @classmethod
    def from_entity(cls, llm_call) -> "LlmCallResponse":
        """Создать DTO из доменной сущности LlmCall."""
        return cls(
            id=llm_call.id,
            call_id=llm_call.call_id,
            attempt_number=llm_call.attempt_number,
            agent_name=llm_call.agent_name,
            model=llm_call.model,
            user_id=llm_call.user_id,
            prompt=llm_call.prompt,
            response=llm_call.response,
            temperature=llm_call.temperature,
            response_format=llm_call.response_format,
            status=llm_call.status,
            error_type=llm_call.error_type,
            error_message=llm_call.error_message,
            duration_ms=llm_call.duration_ms,
            prompt_tokens=llm_call.prompt_tokens,
            completion_tokens=llm_call.completion_tokens,
            total_tokens=llm_call.total_tokens,
            response_size_bytes=llm_call.response_size_bytes,
            cost_usd=llm_call.cost_usd,
            context=llm_call.context,
            created_at=llm_call.created_at,
        )


class LlmCallListResponse(BaseModel):
    """Ответ со списком вызовов LLM."""

    items: list[LlmCallResponse] = Field(..., description="Список вызовов")
    total: int = Field(..., description="Общее количество записей")
    page: int = Field(..., description="Текущая страница")
    page_size: int = Field(..., description="Размер страницы")
