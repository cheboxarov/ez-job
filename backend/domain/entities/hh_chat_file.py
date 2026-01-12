from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(slots=True)
class HHChatFile:
    """Файл, прикрепленный к сообщению чата HH."""

    url: str
    title: str
    content_type: str
    upload_id: str
    preview: Optional[Dict[str, Any]] = None
    properties: Optional[Dict[str, Any]] = None
