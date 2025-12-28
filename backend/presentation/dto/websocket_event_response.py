"""DTO для WebSocket событий."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from pydantic import BaseModel, Field


class WebSocketEventResponse(BaseModel):
    """DTO для WebSocket события."""

    event_type: str = Field(..., description="Тип события")
    payload: Dict[str, Any] = Field(..., description="Данные события")
    created_at: str = Field(..., description="Время создания события (ISO format)")


class AgentActionCreatedPayload(BaseModel):
    """Payload для события agent_action_created."""

    id: str
    type: str
    entity_type: str
    entity_id: int
    created_by: str
    user_id: str
    resume_hash: str | None
    data: Dict[str, Any]
    created_at: str
    updated_at: str
    is_read: bool


class VacancyResponseCreatedPayload(BaseModel):
    """Payload для события vacancy_response_created."""

    id: str
    vacancy_id: int
    resume_id: str
    resume_hash: str | None
    user_id: str
    cover_letter: str
    vacancy_name: str
    vacancy_url: str | None
    created_at: str | None
