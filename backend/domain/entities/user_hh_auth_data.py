"""Доменная сущность для HH auth data пользователя."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class UserHhAuthData:
    """Доменная сущность для хранения HH headers/cookies пользователя.

    Хранит персональные headers и cookies для запросов к HH API.
    """

    user_id: UUID
    headers: dict[str, str]
    cookies: dict[str, str]
    cookies_updated_at: datetime | None = None
