"""Pydantic схемы для FastAPI Users."""

from __future__ import annotations

from uuid import UUID

from fastapi_users import schemas


class UserRead(schemas.BaseUser[UUID]):
    """Схема для чтения пользователя."""

    pass


class UserCreate(schemas.BaseUserCreate):
    """Схема для создания пользователя."""

    pass


class UserUpdate(schemas.BaseUserUpdate):
    """Схема для обновления пользователя."""

    pass

