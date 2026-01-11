"""Инструмент для генерации уточняющих вопросов."""

from __future__ import annotations

from typing import List
from uuid import uuid4

from domain.entities.resume_edit_question import ResumeEditQuestion


def generate_question(text: str, required: bool = True) -> ResumeEditQuestion:
    """Сгенерировать вопрос.

    Args:
        text: Текст вопроса.
        required: Обязателен ли ответ.

    Returns:
        ResumeEditQuestion.
    """
    return ResumeEditQuestion(
        id=uuid4(),
        text=text,
        required=required,
    )


def generate_questions_for_metrics(
    context: str | None = None,
) -> List[ResumeEditQuestion]:
    """Сгенерировать вопросы про метрики и результаты.

    Args:
        context: Контекст (например, название компании или проекта).

    Returns:
        Список вопросов.
    """
    questions: List[ResumeEditQuestion] = []

    if context:
        questions.append(
            generate_question(
                f"Какие конкретные метрики или результаты можно указать для {context}? "
                "Например, процент улучшения, количество пользователей, объем данных и т.д.",
                required=True,
            )
        )
    else:
        questions.append(
            generate_question(
                "Какие конкретные метрики или результаты можно указать? "
                "Например, процент улучшения производительности, количество пользователей, объем данных и т.д.",
                required=True,
            )
        )

    return questions


def generate_questions_for_stack(context: str | None = None) -> List[ResumeEditQuestion]:
    """Сгенерировать вопросы про стек технологий.

    Args:
        context: Контекст (например, название компании или проекта).

    Returns:
        Список вопросов.
    """
    questions: List[ResumeEditQuestion] = []

    if context:
        questions.append(
            generate_question(
                f"Какие технологии использовались в {context}? "
                "Укажите конкретные языки программирования, фреймворки, библиотеки, инструменты.",
                required=True,
            )
        )
    else:
        questions.append(
            generate_question(
                "Какие технологии использовались? "
                "Укажите конкретные языки программирования, фреймворки, библиотеки, инструменты.",
                required=True,
            )
        )

    return questions


def generate_questions_for_context() -> List[ResumeEditQuestion]:
    """Сгенерировать вопросы про контекст проекта.

    Returns:
        Список вопросов.
    """
    questions: List[ResumeEditQuestion] = []

    questions.append(
        generate_question(
            "Какой был размер команды? Сколько человек работало над проектом?",
            required=False,
        )
    )

    questions.append(
        generate_question(
            "Какие были особенности проекта? Например, высоконагруженная система, "
            "микросервисная архитектура, работа с большими данными и т.д.",
            required=False,
        )
    )

    return questions


def generate_questions_for_missing_data(
    missing_data_type: str,
) -> List[ResumeEditQuestion]:
    """Сгенерировать вопросы для недостающих данных.

    Args:
        missing_data_type: Тип недостающих данных ("metrics", "stack", "context").

    Returns:
        Список вопросов.
    """
    if missing_data_type == "metrics":
        return generate_questions_for_metrics()
    elif missing_data_type == "stack":
        return generate_questions_for_stack()
    elif missing_data_type == "context":
        return generate_questions_for_context()
    else:
        return []
