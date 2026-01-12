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
from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from infrastructure.agents.base_agent import BaseAgent
from infrastructure.agents.resume_edit.tools.extract_sections_tool import extract_sections
from infrastructure.agents.resume_edit.tools.rule_check_tool import (
    check_all_rules,
    load_resume_rules,
)


class _QuestionToolAgent(BaseAgent):
    AGENT_NAME = "DeepAgentsQuestionTool"


class GenerateQuestionsInput(BaseModel):
    """Входные данные для генерации вопросов (resume_text инжектируется)."""

    user_message: str = Field(..., description="Сообщение пользователя.")
    current_task: dict | None = Field(
        default=None, description="Текущая задача плана (опционально)."
    )
    history: list[dict] | None = Field(
        default=None, description="История диалога (опционально)."
    )


class GenerateQuestionsFullInput(BaseModel):
    """Полная схема с resume_text для внутреннего вызова инструмента."""

    resume_text: str = Field(..., description="Текст резюме.")
    user_message: str = Field(..., description="Сообщение пользователя.")
    user_id: UUID | None = Field(default=None, description="ID пользователя (опционально).")
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


def create_deepagents_question_tool(
    config: OpenAIConfig, unit_of_work: UnitOfWorkPort | None = None
):
    """Создать инструмент LangChain для генерации вопросов."""
    helper = _QuestionToolAgent(config, unit_of_work=unit_of_work)
    prompt = _load_prompt()

    @tool("generate_resume_questions", args_schema=GenerateQuestionsFullInput)
    async def generate_questions_tool(
        resume_text: str,
        user_message: str,
        user_id: UUID | None = None,
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
О себе: {sections.get('about', 'не найдено')}
Опыт: {sections.get('experience', 'не найдено')}

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
        user_prompt = """Сгенерируй уточняющие вопросы в формате JSON.

КРИТИЧЕСКИ ВАЖНО: Верни ТОЛЬКО валидный JSON-объект. НЕ возвращай обычный текст, НЕ возвращай промежуточные размышления.

Обязательный формат ответа:
{
  "action": "ask_question",
  "assistant_message": "Текст сообщения для пользователя",
  "questions": [
    {
      "id": "uuid",
      "text": "Текст вопроса",
      "required": true,
      "suggested_answers": ["вариант 1", "вариант 2", "не знаю, придумай сам"],
      "allow_multiple": false
    }
  ],
  "patches": [],
  "warnings": []
}

Все поля обязательны. Поле "questions" должно содержать минимум 1 вопрос. Поле "patches" всегда пустое []."""

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

        context = {
            "use_case": "resume_edit_question_tool",
            "task_id": current_task.get("id") if current_task else None,
        }

        response = await helper._call_llm_with_retry(
            messages=messages,
            parse_func=parse_func,
            validate_func=None,  # Валидация после, retry бессмысленен без изменения промпта
            temperature=0.4,
            response_format={"type": "json_object"},
            user_id=user_id,
            context=context,
        )

        # Нормализация ответа: исправляем неправильный action
        if response.get("action") != "ask_question":
            log.warning(
                f"Неверный action от QuestionTool: {response.get('action')}, исправляем на ask_question"
            )
            response["action"] = "ask_question"

        # Нормализация вопросов: добавляем suggested_answers если отсутствует
        for q in response.get("questions", []):
            if not q.get("suggested_answers"):
                log.warning(f"Вопрос без вариантов ответа: {q.get('text')}, добавляем дефолтные")
                q["suggested_answers"] = ["Да", "Нет", "Не знаю, придумай сам"]

        questions_data = response.get("questions", [])

        # Если вопросов нет, добавляем warning (вместо бессмысленного retry)
        if not questions_data:
            log.warning("QuestionTool не вернул вопросы")
            response.setdefault("warnings", []).append(
                "Агент не сгенерировал уточняющие вопросы."
            )

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
