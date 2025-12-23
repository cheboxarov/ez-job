"""Доменная сущность для действия агента."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
from uuid import UUID


@dataclass(slots=True)
class AgentAction:
    """Действие агента.

    Содержит тип действия и данные, необходимые для его выполнения.
    """

    id: UUID
    """Уникальный идентификатор действия."""

    type: str
    """Тип действия (например, "send_message", "create_event")."""

    entity_type: str
    """Тип сущности, к которой относится действие (например, "hh_dialog")."""

    entity_id: int
    """ID сущности, к которой относится действие (ID диалога)."""

    created_by: str
    """Идентификатор агента, который создал это действие (например, "messages_agent")."""

    user_id: UUID
    """ID пользователя, для которого создано действие."""

    data: Dict[str, Any]
    """Данные действия.
    
    Для "send_message" содержит:
    - dialog_id: int - ID чата
    - message_to: int | None - ID сообщения, на которое отвечаем (опционально)
    - message_text: str - текст сообщения для отправки
    
    Для "create_event" содержит:
    - dialog_id: int - ID чата
    - event_type: str - тип события:
      * "call_request" - запрос на созвон/встречу/собеседование
      * "external_action_request" - когда требуется действие вне чата HH (анкета, форма и т.д.)
    - message: str - краткое описание от LLM, что требуется сделать или куда нас зовут
    """

    created_at: datetime
    """Время создания действия."""

    updated_at: datetime
    """Время последнего обновления действия."""

    resume_hash: str | None = None
    """Hash резюме, использованного при создании действия (опционально)."""
