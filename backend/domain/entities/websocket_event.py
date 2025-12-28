"""Доменная сущность для WebSocket событий."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
from uuid import UUID


@dataclass(slots=True)
class WebSocketEvent:
    """Базовое событие для WebSocket.
    
    Используется для передачи событий от бэкенда к фронтенду через WebSocket соединение.
    """

    event_type: str
    """Тип события (например, "agent_action_created", "vacancy_response_created")."""

    user_id: UUID
    """ID пользователя, которому предназначено событие."""

    payload: Dict[str, Any]
    """Данные события (сериализованная сущность в виде словаря)."""

    created_at: datetime
    """Время создания события."""
