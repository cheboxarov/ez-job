"""DTO для ответа с HH auth data."""

from __future__ import annotations

from typing import Dict

from pydantic import BaseModel, Field

from domain.entities.user_hh_auth_data import UserHhAuthData


class HhAuthResponse(BaseModel):
    """DTO для ответа с HH auth data пользователя."""

    headers: Dict[str, str] = Field(
        ...,
        description="HH API headers в формате JSON",
    )
    cookies: Dict[str, str] = Field(
        ...,
        description="HH API cookies в формате JSON",
    )

    @classmethod
    def from_entity(cls, entity: UserHhAuthData) -> "HhAuthResponse":
        """Создает DTO из доменной сущности.

        Args:
            entity: Доменная сущность UserHhAuthData.

        Returns:
            DTO для JSON ответа.
        """
        return cls(
            headers=entity.headers,
            cookies=entity.cookies,
        )
