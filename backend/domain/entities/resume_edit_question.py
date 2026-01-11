"""Доменная сущность вопроса для редактирования резюме."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List
from uuid import UUID, uuid4


@dataclass(slots=True)
class ResumeEditQuestion:
    """Вопрос агента к пользователю для уточнения деталей редактирования.

    Агент задает вопросы, когда ему не хватает данных для генерации правок
    (метрики, стек технологий, контекст проекта и т.д.).
    """

    id: UUID
    """Уникальный идентификатор вопроса."""

    text: str
    """Текст вопроса."""

    required: bool = True
    """Обязателен ли ответ на вопрос перед продолжением."""

    suggested_answers: List[str] = field(default_factory=list)
    """Варианты ответов, предлагаемые LLM для быстрого выбора."""

    allow_multiple: bool = False
    """Разрешить ли выбор нескольких ответов для этого вопроса."""

    def __post_init__(self) -> None:
        """Генерируем ID, если не передан."""
        if not isinstance(self.id, UUID):
            self.id = uuid4()
