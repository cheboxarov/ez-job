from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SuggestedUserFilterSettings:
    """Предложенные (AI) настройки фильтров пользователя.

    Используются только как результат генерации и не содержат user_id
    и полей, которые мы не хотим автозаполнять.
    """

    text: str | None = None
    salary: int | None = None
    currency: str | None = None

