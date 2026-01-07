"""DTO для админских ответов по пользователям."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from domain.entities.user import User


class AdminUserResponse(BaseModel):
    """Расширенный DTO пользователя для админки."""

    id: UUID = Field(..., description="UUID пользователя")
    email: str | None = Field(None, description="Email пользователя")
    phone: str | None = Field(None, description="Телефон пользователя")
    is_active: bool = Field(..., description="Признак активного пользователя")
    is_superuser: bool = Field(..., description="Признак администратора")
    is_verified: bool = Field(..., description="Признак подтверждённого email")
    created_at: str | None = Field(
        None, description="Дата создания пользователя в ISO формате"
    )

    @classmethod
    def from_entity(cls, user: User) -> "AdminUserResponse":
        return cls(
            id=user.id,
            email=user.email,
            phone=user.phone,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            is_verified=user.is_verified,
            created_at=user.created_at.isoformat() if user.created_at else None,
        )


class AdminUserListResponse(BaseModel):
    """DTO списка пользователей для админки с пагинацией."""

    items: list[AdminUserResponse] = Field(..., description="Список пользователей")
    total: int = Field(..., description="Общее количество пользователей под фильтром")
    page: int = Field(..., description="Текущая страница")
    page_size: int = Field(..., description="Размер страницы")

