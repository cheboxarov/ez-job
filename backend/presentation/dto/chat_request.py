"""DTO для запросов чатов."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class SendChatMessageRequest(BaseModel):
    """DTO для запроса отправки сообщения в чат."""

    text: str = Field(..., description="Текст сообщения для отправки", min_length=1)
    idempotency_key: Optional[str] = Field(None, description="Ключ идемпотентности")
    hhtm_source: str = Field("app", description="Источник запроса")
    hhtm_source_label: str = Field("chat", description="Метка источника")

