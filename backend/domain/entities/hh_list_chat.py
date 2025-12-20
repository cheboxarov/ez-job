from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from domain.entities.hh_chat_message import HHChatMessage


@dataclass(slots=True)
class HHWritePossibility:
    """Возможность писать в чат."""

    name: str
    write_disabled_reasons: List[str]
    write_disabled_reason: str


@dataclass(slots=True)
class HHChatOperations:
    """Доступные операции с чатом."""

    enabled: List[str]


@dataclass(slots=True)
class HHChatListItem:
    """Элемент списка чатов из /chatik/api/chats."""

    id: int
    type: str
    unread_count: int
    pinned: bool
    notification_enabled: bool
    creation_time: str
    idempotency_key: str
    owner_violates_rules: bool
    untrusted_employer_restrictions_applied: bool
    current_participant_id: str
    last_activity_time: Optional[str] = None

    last_message: Optional[HHChatMessage] = None
    last_viewed_by_opponent_message_id: Optional[int] = None
    last_viewed_by_current_user_message_id: Optional[int] = None
    resources: Optional[Dict[str, List[str]]] = None
    write_possibility: Optional[HHWritePossibility] = None
    operations: Optional[HHChatOperations] = None
    participants_ids: Optional[List[str]] = None
    online_until_time: Optional[str] = None
    block_chat_info: Optional[List[Dict[str, Any]]] = None


@dataclass(slots=True)
class HHChatDisplayInfo:
    """Информация для отображения чата."""

    title: str
    subtitle: Optional[str] = None
    icon: Optional[str] = None


@dataclass(slots=True)
class HHListChat:
    """Список чатов из /chatik/api/chats."""

    items: List[HHChatListItem]
    display_info: Dict[int, HHChatDisplayInfo]
