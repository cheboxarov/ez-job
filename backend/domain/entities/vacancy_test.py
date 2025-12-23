"""Доменная сущность теста вакансии."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(slots=True)
class VacancyTestQuestionOption:
    """Вариант ответа для select вопроса."""

    value: str  # ID варианта ответа (например, "296586239")
    text: str  # Текст варианта ответа (например, "Да")


@dataclass(slots=True)
class VacancyTestQuestion:
    """Вопрос из теста вакансии."""

    task_id: str  # ID задачи (например, "291683492")
    question_text: str  # Текст вопроса
    field_name: str  # Имя поля формы (например, "task_291683492" для select или "task_291683492_text" для text)
    question_type: str  # Тип вопроса: "select" для radio кнопок, "text" для textarea
    options: Optional[List[VacancyTestQuestionOption]] = None  # Варианты ответов для select вопросов


@dataclass(slots=True)
class VacancyTest:
    """Тест вакансии с вопросами."""

    questions: List[VacancyTestQuestion]  # Список вопросов
    uid_pk: Optional[str] = None  # uidPk из формы
    guid: Optional[str] = None  # guid из формы
    start_time: Optional[str] = None  # startTime из формы
    test_required: bool = False  # testRequired из формы
    description: Optional[str] = None  # Описание теста (из data-qa="test-description")

