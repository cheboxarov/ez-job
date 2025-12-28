"""Доменная сущность резюме."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class Resume:
    """Доменная сущность резюме.

    Главная сущность для хранения резюме пользователя.
    Содержит текст резюме и дополнительные пользовательские параметры фильтрации.
    """

    id: UUID
    user_id: UUID
    content: str
    user_parameters: str | None = None
    external_id: str | None = None
    headhunter_hash: str | None = None
    is_auto_reply: bool = False
    autolike_threshold: int = 50