"""Sub-agent для генерации уточняющих вопросов."""

from __future__ import annotations

from pathlib import Path

from loguru import logger


def _load_prompt() -> str:
    prompt_path = (
        Path(__file__).parent.parent.parent
        / "prompts"
        / "resume_edit_question_agent.md"
    )
    try:
        base_prompt = prompt_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning(f"Промпт не найден: {prompt_path}, используем базовый")
        base_prompt = "Ты AI-ассистент для уточнения деталей резюме."

    appendix = """

## ВАЖНО ДЛЯ DEEPAGENTS

Ты получаешь одно входное сообщение. В нём передаются данные (обычно JSON) с полями:
- user_message
- user_id
- current_task
- history

`resume_text` передается автоматически из state, не нужно его передавать.

Твои действия:
1. Извлеки эти поля из входа.
2. Вызови инструмент generate_resume_questions с этими параметрами (user_id опционально).
3. Верни результат инструмента БЕЗ ИЗМЕНЕНИЙ в виде JSON.

КРИТИЧЕСКИ ВАЖНО: Верни ТОЛЬКО валидный JSON-объект. НЕ возвращай обычный текст, НЕ возвращай промежуточные размышления.

Обязательный формат ответа:
{
  "action": "ask_question",
  "assistant_message": "Текст сообщения",
  "questions": [...],
  "patches": [],
  "warnings": []
}

Если вход не JSON, аккуратно распознай блоки с данными.
"""
    return f"{base_prompt}\n{appendix}"


def create_question_subagent(tools: list) -> dict:
    """Создать спецификацию Question Sub-Agent."""
    return {
        "name": "question-agent",
        "description": "Задает уточняющие вопросы для редактирования резюме.",
        "system_prompt": _load_prompt(),
        "tools": tools,
    }
