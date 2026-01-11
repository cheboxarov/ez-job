"""Доменная сущность patch-операции для редактирования резюме."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class ResumeEditPatch:
    """Patch-операция для редактирования резюме.

    Представляет одно изменение в тексте резюме: замену, вставку или удаление.
    Использует построчную систему с нумерацией строк (1-based).
    """

    type: Literal["replace", "insert", "delete"]
    """Тип операции: replace (замена), insert (вставка), delete (удаление)."""

    start_line: int
    """Номер начальной строки (1-based, обязательное)."""

    end_line: int
    """Номер конечной строки (1-based, обязательное). Для insert может быть равен start_line."""

    old_text: str
    """Текст, который нужно заменить/удалить. Для insert может быть пустой строкой."""

    reason: str
    """Объяснение изменения (почему это изменение было сделано)."""

    new_text: str | None = None
    """Новый текст (None для delete)."""

    id: str | None = None
    """Уникальный идентификатор patch (генерируется на бэке)."""
