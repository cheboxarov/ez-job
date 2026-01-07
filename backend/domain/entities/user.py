"""Доменная сущность пользователя."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class User:
    """Доменная сущность пользователя.

    Хранит минимальный профиль пользователя для бизнес-логики сервиса.
    Резюме вынесено в отдельную сущность Resume.
    Настройки поиска вакансий вынесены в отдельную сущность ResumeFilterSettings.

    Для админских сценариев сущность расширена базовыми полями профиля
    и флагами статуса, чтобы не тянуть инфраструктурную модель UserModel
    в домен.
    """

    id: UUID
    email: str | None = None
    phone: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    created_at: datetime | None = None