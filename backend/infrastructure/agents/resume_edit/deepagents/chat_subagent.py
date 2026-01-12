"""Sub-agent для общего диалога при редактировании резюме."""

from __future__ import annotations

from pathlib import Path

from loguru import logger


def _load_prompt() -> str:
    prompt_path = (
        Path(__file__).parent.parent.parent / "prompts" / "resume_edit_chat_agent.md"
    )
    try:
        base_prompt = prompt_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning(f"Промпт не найден: {prompt_path}, используем базовый")
        base_prompt = "Ты дружелюбный AI-ассистент."

    appendix = """

## ВАЖНО ДЛЯ DEEPAGENTS

Ты получаешь одно входное сообщение. 

КРИТИЧЕСКИ ВАЖНО: Верни ТОЛЬКО валидный JSON-объект. НЕ возвращай обычный текст, НЕ возвращай промежуточные размышления.

Обязательный формат ответа:
{
  "action": "chat",
  "assistant_message": "Текст ответа пользователю",
  "questions": [],
  "patches": [],
  "warnings": []
}

Все поля обязательны. Поле "questions" всегда пустое []. Поле "patches" всегда пустое [].
"""
    return f"{base_prompt}\n{appendix}"


def create_chat_subagent(tools: list) -> dict:
    """Создать спецификацию Chat Sub-Agent."""
    return {
        "name": "chat-agent",
        "description": "Обеспечивает общий диалог при редактировании резюме.",
        "system_prompt": _load_prompt(),
        "tools": tools,
    }
