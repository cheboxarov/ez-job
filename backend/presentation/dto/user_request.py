"""DTO для запросов пользователя."""

from __future__ import annotations

from pydantic import BaseModel


class UpdateUserRequest(BaseModel):
    """DTO для обновления пользователя.

    User теперь содержит только id, обновлять нечего.
    Оставлено для совместимости с API.
    """

