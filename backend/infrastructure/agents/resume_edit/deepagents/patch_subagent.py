"""Sub-agent для генерации патчей редактирования резюме."""

from __future__ import annotations

from pathlib import Path

from loguru import logger


def _load_prompt() -> str:
    prompt_path = (
        Path(__file__).parent.parent.parent
        / "prompts"
        / "resume_edit_patch_agent.md"
    )
    try:
        base_prompt = prompt_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning(f"Промпт не найден: {prompt_path}, используем базовый")
        base_prompt = "Ты AI-ассистент для внесения правок в резюме."

    appendix = """

## ВАЖНО ДЛЯ DEEPAGENTS

Ты получаешь одно входное сообщение. В нём передаются данные (обычно JSON) с полями:
- resume_text
- user_message
- current_task
- history

Твои действия:
1. Извлеки эти поля из входа.
2. Вызови инструмент generate_resume_patches с этими параметрами.
3. Верни результат инструмента БЕЗ ИЗМЕНЕНИЙ в виде JSON.

Если вход не JSON, аккуратно распознай блоки с данными.
"""
    return f"{base_prompt}\n{appendix}"


def create_patch_subagent(tools: list) -> dict:
    """Создать спецификацию Patch Sub-Agent."""
    return {
        "name": "patch-agent",
        "description": "Генерирует патчи для редактирования резюме.",
        "system_prompt": _load_prompt(),
        "tools": tools,
    }
