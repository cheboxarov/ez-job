from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(slots=True)
class HHWorkflowTransition:
    """Переход workflow для сообщения."""

    id: int
    topic_id: int
    applicant_state: str
    declined_by_applicant: bool


@dataclass(slots=True)
class HHParticipantDisplay:
    """Отображение участника чата."""

    name: str
    is_bot: bool


@dataclass(slots=True)
class HHChatMessage:
    """Сообщение в чате HH."""

    id: int
    chat_id: int
    creation_time: str
    text: str
    type: str
    can_edit: bool
    can_delete: bool
    only_visible_for_my_type: bool
    has_content: bool
    hidden: bool

    workflow_transition_id: Optional[int] = None
    workflow_transition: Optional[HHWorkflowTransition] = None
    participant_display: Optional[HHParticipantDisplay] = None
    participant_id: Optional[str] = None
    resources: Optional[Dict[str, List[str]]] = None
