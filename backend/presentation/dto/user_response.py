"""DTO для ответов пользователя."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from domain.entities.user import User


class UserResponse(BaseModel):
    """DTO для представления пользователя в JSON ответе."""

    id: UUID = Field(..., description="UUID пользователя")

    @classmethod
    def from_entity(cls, user: User) -> "UserResponse":
        """Создает DTO из доменной сущности пользователя.

        Args:
            user: Доменная сущность User.

        Returns:
            DTO для JSON ответа.
        """
        return cls(id=user.id)

