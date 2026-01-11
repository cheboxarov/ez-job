"""Инструмент для проверки правил HH.ru."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List


def load_resume_rules() -> str:
    """Загрузить правила из файла.

    Returns:
        Текст правил.
    """
    rules_path = Path(__file__).parent.parent.parent / "prompts" / "resume_rules.md"
    try:
        return rules_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "Правила не найдены"


def check_rule(
    resume_text: str, rule_name: str, section: str | None = None
) -> Dict[str, any]:
    """Проверить конкретное правило для резюме.

    Args:
        resume_text: Текст резюме.
        section: Секция резюме для проверки (опционально).

    Returns:
        Словарь с результатом проверки: {"passed": bool, "issues": List[str], "suggestions": List[str]}
    """
    text_to_check = section if section else resume_text
    issues: List[str] = []
    suggestions: List[str] = []

    # Проверка на длинное тире
    if "—" in text_to_check:
        issues.append("Найдено длинное тире (—) - признак AI-генерации")
        suggestions.append("Заменить длинное тире (—) на обычный дефис (-)")

    # Проверка на процессные глаголы
    process_verbs = ["участвую", "тестирую", "разрабатываю", "работаю над"]
    found_verbs = []
    for verb in process_verbs:
        if verb in text_to_check.lower():
            found_verbs.append(verb)

    if found_verbs:
        issues.append(f"Найдены процессные глаголы: {', '.join(found_verbs)}")
        suggestions.append(
            "Заменить процессные глаголы на глаголы совершенного вида (сделал, реализовал, внедрил)"
        )

    # Проверка на "ровные" проценты
    even_percent_pattern = re.compile(r"\b(20|30|40|50|60|70|80|90|100)%\b")
    if even_percent_pattern.search(text_to_check):
        issues.append("Найдены 'ровные' проценты (20%, 50% и т.д.) - выглядят вымышленно")
        suggestions.append("Использовать более реалистичные проценты (например, 23%, 47%)")

    # Проверка на шаблонные формулировки
    template_phrases = [
        "разработал реферальную систему",
        "модуль квестов",
        "партнерскую интеграцию",
        "оптимизировал количество записей",
    ]
    found_templates = []
    for phrase in template_phrases:
        if phrase.lower() in text_to_check.lower():
            found_templates.append(phrase)

    if found_templates:
        issues.append(f"Найдены шаблонные формулировки: {', '.join(found_templates)}")
        suggestions.append("Переформулировать уникальным образом")

    # Проверка на GPT-символы
    gpt_symbols = ["~", "•", "→"]
    found_symbols = []
    for symbol in gpt_symbols:
        if symbol in text_to_check:
            found_symbols.append(symbol)

    if found_symbols:
        issues.append(f"Найдены GPT-символы: {', '.join(found_symbols)}")
        suggestions.append("Удалить спецсимволы от ChatGPT")

    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "suggestions": suggestions,
    }


def check_all_rules(resume_text: str) -> Dict[str, any]:
    """Проверить все правила для резюме.

    Args:
        resume_text: Текст резюме.

    Returns:
        Словарь с результатами проверки всех правил.
    """
    from infrastructure.agents.resume_edit.tools.extract_sections_tool import (
        extract_sections,
    )

    sections = extract_sections(resume_text)
    all_issues: List[str] = []
    all_suggestions: List[str] = []

    # Проверяем каждую секцию
    for section_name, section_text in sections.items():
        if section_text:
            result = check_rule(resume_text, "all", section_text)
            if result["issues"]:
                all_issues.extend(
                    [f"[{section_name}]: {issue}" for issue in result["issues"]]
                )
                all_suggestions.extend(result["suggestions"])

    # Проверяем весь текст
    full_result = check_rule(resume_text, "all")
    all_issues.extend(full_result["issues"])
    all_suggestions.extend(full_result["suggestions"])

    return {
        "passed": len(all_issues) == 0,
        "issues": all_issues,
        "suggestions": list(set(all_suggestions)),  # Убираем дубликаты
    }
