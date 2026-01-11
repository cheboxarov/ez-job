"""LangChain tool для генерации патчей редактирования резюме."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from loguru import logger
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from config import OpenAIConfig
from infrastructure.agents.base_agent import BaseAgent
from infrastructure.agents.resume_edit.tools.build_patch_tool import (
    build_patches_from_changes,
)
from infrastructure.agents.resume_edit.tools.extract_sections_tool import extract_sections
from infrastructure.agents.resume_edit.tools.format_resume_tool import (
    format_resume_with_line_numbers,
)
from infrastructure.agents.resume_edit.tools.rule_check_tool import (
    check_all_rules,
    load_resume_rules,
)
from infrastructure.agents.resume_edit.tools.validate_patch_tool import (
    validate_patch,
    validate_patches,
)


class _PatchToolAgent(BaseAgent):
    AGENT_NAME = "DeepAgentsPatchTool"


class GeneratePatchesInput(BaseModel):
    """Входные данные для генерации патчей."""

    resume_text: str = Field(..., description="Текст резюме.")
    user_message: str = Field(..., description="Сообщение пользователя.")
    current_task: dict | None = Field(
        default=None, description="Текущая задача плана (опционально)."
    )
    history: list[dict] | None = Field(
        default=None, description="История диалога (опционально)."
    )


def _load_prompt() -> str:
    prompt_path = (
        Path(__file__).parent.parent.parent / "prompts" / "resume_edit_patch_agent.md"
    )
    try:
        return prompt_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning(f"Промпт не найден: {prompt_path}, используем базовый")
        return "Ты AI-ассистент для внесения правок в резюме."


def create_deepagents_patch_tool(config: OpenAIConfig):
    """Создать инструмент LangChain для генерации патчей."""
    helper = _PatchToolAgent(config)
    prompt = _load_prompt()

    @tool("generate_resume_patches", args_schema=GeneratePatchesInput)
    async def generate_patches_tool(
        resume_text: str,
        user_message: str,
        current_task: dict | None = None,
        history: list[dict] | None = None,
    ) -> dict[str, Any]:
        log = logger

        log.info(
            f"[DeepAgentsPatchTool] Генерация патчей для задачи: "
            f"{current_task.get('title') if current_task else 'Unknown'}"
        )

        sections = extract_sections(resume_text)
        rules_check = check_all_rules(resume_text)
        resume_rules = load_resume_rules()
        numbered_resume = format_resume_with_line_numbers(resume_text)

        history_context = ""
        if history:
            history_context = "\n".join(
                [
                    f"Пользователь: {msg.get('user', '')}\nАгент: {msg.get('assistant', '')}"
                    for msg in history[-10:]
                ]
            )

        system_prompt = f"""{prompt}

ТЕКУЩЕЕ РЕЗЮМЕ (с нумерацией строк):
{numbered_resume}

СЕКЦИИ:
О себе: {sections.get('about', 'не найдено')[:300]}...
Опыт: {sections.get('experience', 'не найдено')[:300]}...

ПРОБЛЕМЫ:
{json.dumps(rules_check.get('issues', []), ensure_ascii=False, indent=2)}

ПРАВИЛА HH:
{resume_rules}

ТЕКУЩАЯ ЗАДАЧА (ФОКУСИРУЙСЯ НА НЕЙ):
{json.dumps(current_task, ensure_ascii=False, indent=2) if current_task else 'Нет задачи'}

ИСТОРИЯ:
{history_context}

СООБЩЕНИЕ ПОЛЬЗОВАТЕЛЯ (ДАННЫЕ ДЛЯ ПРАВОК):
{user_message}
"""
        user_prompt = "Сгенерируй патчи в формате JSON."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        def parse_func(content: str) -> dict[str, Any]:
            try:
                return json.loads(content)
            except json.JSONDecodeError as exc:
                log.error(f"Ошибка парсинга JSON: {exc}")
                return {
                    "action": "generate_patches",
                    "assistant_message": "Не удалось сгенерировать правки из-за ошибки формата. Попробуйте еще раз.",
                    "patches": [],
                    "warnings": ["Ошибка парсинга ответа LLM"],
                }

        def validate_func(result: dict[str, Any]) -> bool:
            if result.get("action") != "generate_patches":
                log.warning(
                    f"Неверный action от PatchTool: {result.get('action')}"
                )
                return True
            if not result.get("patches") and not result.get("warnings"):
                log.warning("PatchTool вернул пустой список патчей без предупреждений")
                return True
            return False

        context = {
            "use_case": "resume_edit_patch_tool",
            "task_id": current_task.get("id") if current_task else None,
        }

        response = await helper._call_llm_with_retry(
            messages=messages,
            parse_func=parse_func,
            validate_func=validate_func,
            temperature=0.2,
            response_format={"type": "json_object"},
            context=context,
        )

        patches_data = response.get("patches", [])
        if not patches_data:
            if not response.get("warnings"):
                response["warnings"] = ["Агент не сгенерировал патчи."]
            response["patches"] = []
            response.setdefault("questions", [])
            return response

        patches = build_patches_from_changes(resume_text, patches_data)
        if not patches:
            log.warning("[DeepAgentsPatchTool] Не удалось построить патчи из данных LLM")
            response["patches"] = []
            response.setdefault("warnings", []).append(
                "Не удалось найти места для вставки изменений в тексте."
            )
            response.setdefault("questions", [])
            return response

        for patch in patches:
            if not patch.id:
                patch.id = str(uuid4())

        valid_patches = []
        invalid_errors = []
        for patch in patches:
            is_valid, error = validate_patch(
                patch=patch, resume_text=resume_text, max_changed_lines_percent=25.0
            )
            if is_valid:
                valid_patches.append(patch)
            else:
                invalid_errors.append(error or "Невалидный патч")

        if invalid_errors:
            response.setdefault("warnings", []).extend(
                [f"Патч отклонен: {e}" for e in invalid_errors]
            )

        if not valid_patches:
            response["patches"] = []
            response.setdefault("questions", [])
            return response

        is_valid_group, group_errors = validate_patches(
            patches=valid_patches,
            resume_text=resume_text,
            max_changed_lines_percent=25.0,
            max_patch_items=12,
        )

        if not is_valid_group:
            response.setdefault("warnings", []).extend(group_errors)

        response["patches"] = [
            {
                "id": patch.id or "",
                "type": patch.type,
                "start_line": patch.start_line,
                "end_line": patch.end_line,
                "old_text": patch.old_text,
                "new_text": patch.new_text,
                "reason": patch.reason,
            }
            for patch in valid_patches
        ]

        response.setdefault("questions", [])
        response.setdefault("warnings", [])

        return response

    return generate_patches_tool
