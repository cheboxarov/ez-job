"""Доменная сущность результата редактирования резюме."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from domain.entities.resume_edit_patch import ResumeEditPatch
from domain.entities.resume_edit_question import ResumeEditQuestion


@dataclass(slots=True)
class ResumeEditResult:
    """Результат генерации правок для резюме.

    Содержит сообщение агента, список вопросов (если нужны уточнения),
    список patch-операций и предупреждения.
    """

    assistant_message: str
    """Сообщение от агента с объяснением предложенных изменений."""

    questions: List[ResumeEditQuestion] = field(default_factory=list)
    """Список вопросов для уточнения (если данных недостаточно)."""

    patches: List[ResumeEditPatch] = field(default_factory=list)
    """Список patch-операций для применения."""

    plan: List[dict] = field(default_factory=list)
    """Текущий план выполнения задач (Todo List)."""

    warnings: List[str] = field(default_factory=list)
    """Список предупреждений (например, о лимитах на изменения)."""
