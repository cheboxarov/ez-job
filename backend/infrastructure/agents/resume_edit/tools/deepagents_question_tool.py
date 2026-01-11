"""LangChain tool для генерации вопросов при редактировании резюме."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from loguru import logger
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from config import OpenAIConfig
from domain.entities.resume_edit_question import ResumeEditQuestion
from infrastructure.agents.base_agent import BaseAgent
from infrastructure.agents.resume_edit.tools.extract_sections_tool import extract_sections
from infrastructure.agents.resume_edit.tools.rule_check_tool import (
    check_all_rules,
    load_resume_rules,
)


class _QuestionToolAgent(BaseAgent):
    AGENT_NAME = "DeepAgentsQuestionTool"


class GenerateQuestionsInput(BaseModel):
    """Входные данные для генерации вопросов."""

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
        Path(__file__).parent.parent.parent
        / "prompts"
        / "resume_edit_question_agent.md"
    )
    try:
        return prompt_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning(f"Промпт не найден: {prompt_path}, используем базовый")
        return "Ты AI-ассистент для уточнения деталей резюме."


def create_deepagents_question_tool(config: OpenAIConfig):
    """Создать инструмент LangChain для генерации вопросов."""
    helper = _QuestionToolAgent(config)
    prompt = _load_prompt()

    @tool("generate_resume_questions", args_schema=GenerateQuestionsInput)
    async def generate_questions_tool(
        resume_text: str,
        user_message: str,
        current_task: dict | None = None,
        history: list[dict] | None = None,
    ) -> dict[str, Any]:
        log = logger

        log.info(
            f"[DeepAgentsQuestionTool] Генерация вопросов для задачи: "
            f"{current_task.get('title') if current_task else 'Unknown'}"
        )

        sections = extract_sections(resume_text)
        rules_check = check_all_rules(resume_text)
        resume_rules = load_resume_rules()

        history_context = ""
        if history:
            history_context = "\n".join(
                [
                    f"Пользователь: {msg.get('user', '')}\nАгент: {msg.get('assistant', '')}"
                    for msg in history[-10:]
                ]
            )

        system_prompt = f"""{prompt}

ТЕКУЩЕЕ РЕЗЮМЕ:
{resume_text}

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

СООБЩЕНИЕ ПОЛЬЗОВАТЕЛЯ:
{user_message}
"""
        user_prompt = "Сгенерируй уточняющие вопросы в формате JSON."

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
                    "action": "ask_question",
                    "assistant_message": "Не удалось сформулировать вопросы. Попробуйте уточнить запрос.",
                    "questions": [],
                    "warnings": ["Ошибка парсинга ответа LLM"],
                }

        def validate_func(result: dict[str, Any]) -> bool:
            if result.get("action") != "ask_question":
                log.warning(
                    f"Неверный action от QuestionTool: {result.get('action')}"
                )
                return True
            if not result.get("questions"):
                log.warning("QuestionTool не вернул вопросы")
                return True
            for q in result.get("questions", []):
                if not q.get("suggested_answers"):
                    log.warning(f"Вопрос без вариантов ответа: {q.get('text')}")
                    return True
            return False

        context = {
            "use_case": "resume_edit_question_tool",
            "task_id": current_task.get("id") if current_task else None,
        }

        response = await helper._call_llm_with_retry(
            messages=messages,
            parse_func=parse_func,
            validate_func=validate_func,
            temperature=0.7,
            response_format={"type": "json_object"},
            context=context,
        )

        questions_data = response.get("questions", [])
        questions: list[ResumeEditQuestion] = []

        for q_data in questions_data:
            q_text = q_data.get("text", "").strip()
            if not q_text:
                continue

            q_id = q_data.get("id")
            if not q_id:
                q_id = str(uuid4())

            try:
                UUID(q_id)
            except ValueError:
                q_id = str(uuid4())

            questions.append(
                ResumeEditQuestion(
                    id=UUID(q_id),
                    text=q_text,
                    required=q_data.get("required", True),
                    suggested_answers=q_data.get("suggested_answers", []),
                    allow_multiple=q_data.get("allow_multiple", False),
                )
            )

        response["questions"] = [
            {
                "id": str(q.id),
                "text": q.text,
                "required": q.required,
                "suggested_answers": q.suggested_answers,
                "allow_multiple": q.allow_multiple,
            }
            for q in questions
        ]

        response.setdefault("patches", [])
        response.setdefault("warnings", [])

        return response

    return generate_questions_tool
