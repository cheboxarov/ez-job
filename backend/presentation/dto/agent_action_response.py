"""DTO для ответов действий агента."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID

from pydantic import BaseModel, Field

from domain.entities.agent_action import AgentAction


class AgentActionResponse(BaseModel):
    """DTO для действия агента."""

    id: UUID = Field(..., description="Уникальный идентификатор действия")
    type: str = Field(..., description="Тип действия (send_message, create_event и т.д.)")
    entity_type: str = Field(..., description="Тип сущности (hh_dialog и т.д.)")
    entity_id: int = Field(..., description="ID сущности (например, ID диалога)")
    created_by: str = Field(..., description="Идентификатор агента, создавшего действие")
    user_id: UUID = Field(..., description="ID пользователя, для которого создано действие")
    resume_hash: str | None = Field(None, description="Hash резюме, использованного при создании действия")
    data: Dict[str, Any] = Field(..., description="JSON данные действия (зависят от типа действия)")
    created_at: datetime = Field(..., description="Время создания действия")
    updated_at: datetime = Field(..., description="Время последнего обновления действия")

    @classmethod
    def from_entity(cls, action: AgentAction) -> "AgentActionResponse":
        """Создает DTO из доменной сущности AgentAction.

        Args:
            action: Доменная сущность AgentAction.

        Returns:
            DTO для JSON ответа.
        """
        return cls(
            id=action.id,
            type=action.type,
            entity_type=action.entity_type,
            entity_id=action.entity_id,
            created_by=action.created_by,
            user_id=action.user_id,
            resume_hash=action.resume_hash,
            data=action.data,
            created_at=action.created_at,
            updated_at=action.updated_at,
        )


class AgentActionsListResponse(BaseModel):
    """DTO для ответа со списком действий агента."""

    items: List[AgentActionResponse] = Field(..., description="Список действий агента")

