"""Инструмент для выделения секций резюме."""

from __future__ import annotations

import re
from typing import Dict, List


def extract_sections(resume_text: str) -> Dict[str, str]:
    """Выделить секции резюме: "О себе", "Опыт работы", "Навыки", "Образование".

    Args:
        resume_text: Текст резюме.

    Returns:
        Словарь с секциями: {"about": "...", "experience": "...", "skills": "...", "education": "..."}
    """
    sections: Dict[str, str] = {
        "about": "",
        "experience": "",
        "skills": "",
        "education": "",
    }

    lines = resume_text.splitlines()
    current_section: str | None = None
    current_content: List[str] = []

    # Паттерны для поиска секций
    section_patterns = {
        "about": re.compile(
            r"^(о\s+себе|обо\s+мне|о\s+себе|личные\s+качества|про\s+себя)$",
            re.IGNORECASE,
        ),
        "experience": re.compile(
            r"^(опыт\s+работы|трудовой\s+опыт|места\s+работы|работа|опыт)$",
            re.IGNORECASE,
        ),
        "skills": re.compile(
            r"^(навыки|ключевые\s+навыки|технические\s+навыки|компетенции|умения)$",
            re.IGNORECASE,
        ),
        "education": re.compile(
            r"^(образование|обучение|учебные\s+заведения)$",
            re.IGNORECASE,
        ),
    }

    for line in lines:
        line_stripped = line.strip()

        # Проверяем, является ли строка заголовком секции
        found_section = None
        for section_name, pattern in section_patterns.items():
            if pattern.match(line_stripped):
                found_section = section_name
                break

        if found_section:
            # Сохраняем предыдущую секцию
            if current_section and current_content:
                sections[current_section] = "\n".join(current_content).strip()

            # Начинаем новую секцию
            current_section = found_section
            current_content = []
        elif current_section:
            # Добавляем строку в текущую секцию
            if line_stripped:  # Пропускаем пустые строки
                current_content.append(line)

    # Сохраняем последнюю секцию
    if current_section and current_content:
        sections[current_section] = "\n".join(current_content).strip()

    return sections
