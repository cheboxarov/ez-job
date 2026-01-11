"""Агент-планировщик для определения нужных изменений в резюме."""

from __future__ import annotations

import json
from typing import Any, Dict
from uuid import UUID

from loguru import logger

from config import OpenAIConfig
from infrastructure.agents.base_agent import BaseAgent
from infrastructure.agents.resume_edit.tools.extract_sections_tool import extract_sections
from infrastructure.agents.resume_edit.tools.rule_check_tool import check_all_rules


class ResumeEditPlannerAgent(BaseAgent):
    """Агент для планирования изменений резюме.

    Определяет, какие изменения нужны, и решает, задавать ли уточняющие вопросы.
    """

    AGENT_NAME = "ResumeEditPlannerAgent"

    async def plan_edits(
        self,
        resume_text: str,
        user_message: str,
        history: list[dict] | None = None,
        user_id: UUID | None = None,
    ) -> Dict[str, Any]:
        """Спланировать изменения резюме.

        Args:
            resume_text: Текст резюме.
            user_message: Сообщение пользователя с запросом.
            history: История диалога.
            user_id: ID пользователя.

        Returns:
            Словарь с планом: {"needs_questions": bool, "questions": List[str], "changes_needed": List[str]}
        """
        # Извлекаем секции
        sections = extract_sections(resume_text)

        # Проверяем правила
        rules_check = check_all_rules(resume_text)

        # Формируем контекст истории
        history_context = ""
        if history:
            history_context = "\n".join(
                [
                    f"Пользователь: {msg.get('user', '')}\nАгент: {msg.get('assistant', '')}"
                    for msg in history[-5:]  # Последние 5 сообщений
                ]
            )

        system_prompt = """Ты эксперт по редактированию резюме для платформы HH.ru.

Твоя задача - проанализировать запрос пользователя и определить:
1. Какие изменения нужно внести в резюме
2. Нужны ли уточняющие вопросы (если не хватает данных: метрики, стек, контекст)

ПРАВИЛА РЕДАКТИРОВАНИЯ:
- Меняй только конкретные строки/фразы, не переписывай все резюме целиком
- Максимум 25% измененных строк, максимум 12 patch-операций
- Используй якоря текста (минимум 20 символов) для точной привязки
- Если нет конкретных цифр, задавай вопросы и проси подтверждение
- Запрещай длинное тире и шаблонные формулировки

Верни JSON:
{
  "needs_questions": bool,
  "questions": ["вопрос 1", "вопрос 2"],
  "changes_needed": ["изменение 1", "изменение 2"],
  "reasoning": "объяснение решения"
}"""

        user_prompt = f"""Резюме:
{resume_text}

Запрос пользователя: {user_message}

Секции резюме:
О себе: {sections.get('about', 'не найдено')[:200]}...
Опыт: {sections.get('experience', 'не найдено')[:200]}...

Проблемы с правилами:
{json.dumps(rules_check.get('issues', []), ensure_ascii=False, indent=2)}

История диалога:
{history_context if history_context else 'Нет истории'}

Определи, нужны ли уточняющие вопросы и какие изменения требуются."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        def parse_func(content: str) -> Dict[str, Any]:
            return json.loads(content)

        context = {
            "use_case": "plan_resume_edits",
            "resume_length": len(resume_text),
        }

        return await self._call_llm_with_retry(
            messages=messages,
            parse_func=parse_func,
            validate_func=None,
            temperature=0.3,
            response_format={"type": "json_object"},
            user_id=user_id,
            context=context,
        )
