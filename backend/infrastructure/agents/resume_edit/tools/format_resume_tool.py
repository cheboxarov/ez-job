"""Инструмент для форматирования резюме с нумерацией строк."""

from __future__ import annotations

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class FormatResumeInput(BaseModel):
    """Входные данные для форматирования резюме."""

    resume_text: str = Field(..., description="Исходный текст резюме.")


def format_resume_with_line_numbers(resume_text: str) -> str:
    """Форматировать резюме с номерами строк для LLM.

    Формат: [1] Первая строка
            [2] Вторая строка
            ...
    """
    lines = resume_text.splitlines()
    numbered_lines = [f"[{i + 1}] {line}" for i, line in enumerate(lines)]
    return "\n".join(numbered_lines)


@tool("format_resume_with_line_numbers", args_schema=FormatResumeInput)
def format_resume_tool(resume_text: str) -> str:
    """Добавить номера строк к тексту резюме."""
    return format_resume_with_line_numbers(resume_text)
