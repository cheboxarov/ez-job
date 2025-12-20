"""Доменная сущность пользователя."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class User:
    """Доменная сущность пользователя.

    Хранит минимальный профиль пользователя для бизнес-логики сервиса.
    Резюме вынесено в отдельную сущность Resume.
    Настройки поиска вакансий вынесены в отдельную сущность ResumeFilterSettings.
    """

    id: UUID
