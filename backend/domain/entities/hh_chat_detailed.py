from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from domain.entities.hh_chat_message import HHChatMessage


@dataclass(slots=True)
class HHChatMessages:
    """Список сообщений в чате."""

    items: List[HHChatMessage]
    has_more: bool


@dataclass(slots=True)
class HHChatDetailed:
    """Детальная информация о чате из /chatik/api/chat_data."""

    id: int
    type: str
    unread_count: int
    pinned: bool
    notification_enabled: bool
    creation_time: str
    owner_violates_rules: bool
    untrusted_employer_restrictions_applied: bool
    current_participant_id: str
    last_activity_time: Optional[str] = None

    messages: Optional[HHChatMessages] = None
    last_viewed_by_opponent_message_id: Optional[int] = None
    last_viewed_by_current_user_message_id: Optional[int] = None
    resources: Optional[Dict[str, List[str]]] = None
    write_possibility: Optional[Dict[str, Any]] = None
    operations: Optional[Dict[str, Any]] = None
    participants_ids: Optional[List[str]] = None
    online_until_time: Optional[str] = None
    block_chat_info: Optional[List[Dict[str, Any]]] = None
