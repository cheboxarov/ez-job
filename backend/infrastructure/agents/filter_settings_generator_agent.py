from __future__ import annotations

import json
from typing import Any

from openai import AsyncOpenAI
from loguru import logger

from config import OpenAIConfig
from domain.entities.suggested_user_filter_settings import SuggestedUserFilterSettings
from domain.interfaces.filter_settings_generator_service_port import (
    FilterSettingsGeneratorServicePort,
)
from infrastructure.agents.base_agent import BaseAgent


class FilterSettingsGeneratorAgent(BaseAgent, FilterSettingsGeneratorServicePort):
    """LLM-агент для генерации предложенных настроек фильтров пользователя."""

    AGENT_NAME = "FilterSettingsGeneratorAgent"

    async def generate_filter_settings(
        self,
        resume: str,
        user_filter_params: str | None = None,
    ) -> SuggestedUserFilterSettings:
        if not resume or not resume.strip():
            return SuggestedUserFilterSettings()

        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": """Ты ассистент, который помогает кандидату настроить фильтры поиска вакансий.\n\nТебе переданы: текст резюме кандидата и (опционально) его дополнительные пожелания к вакансиям.\n\nТвоя задача — предложить значения только для полей:\n- text (короткий поисковый текст, 1-3 слова),\n- salary (минимальная желаемая зарплата в целых числах),\n- currency (код валюты, например RUR, USD, EUR).\n\nНЕ предлагай регион, опыт, тип занятости, график, роли, сортировку и даты.\n\nВерни строго JSON-объект вида:\n{\n  \"text\": \"Python разработчик\",\n  \"salary\": 200000,\n  \"currency\": \"RUR\"\n}\n\nЛюбое из полей может быть null, если нет уверенности. Никакого другого текста кроме JSON.\n\nДополнительно по форматированию текста в полях:\n- НЕ используй длинное тире (символ '—') ни в одном значении.\n- Если нужно тире, используй только обычный дефис '-'.\n""",
            }
        ]

        user_content_lines: list[str] = ["РЕЗЮМЕ:", resume.strip()]
        if user_filter_params and user_filter_params.strip():
            user_content_lines.append("")
            user_content_lines.append("ДОПОЛНИТЕЛЬНЫЕ ПОЖЕЛАНИЯ:")
            user_content_lines.append(user_filter_params.strip())

        messages.append({"role": "user", "content": "\n".join(user_content_lines)})

        return await self._call_llm_with_retry(
            messages=messages,
            parse_func=self._parse_response,
            validate_func=None,
        )

    def _parse_response(self, content: str) -> SuggestedUserFilterSettings:
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return SuggestedUserFilterSettings()

        if not isinstance(data, dict):
            return SuggestedUserFilterSettings()

        text = data.get("text")
        salary_raw = data.get("salary")
        currency = data.get("currency")

        if isinstance(text, str):
            text_val: str | None = text.strip() or None
        else:
            text_val = None

        salary_val: int | None
        try:
            if salary_raw is None:
                salary_val = None
            else:
                s = int(salary_raw)
                salary_val = s if s > 0 else None
        except (TypeError, ValueError):
            salary_val = None

        if isinstance(currency, str):
            cur = currency.strip().upper()
            currency_val: str | None = cur or None
        else:
            currency_val = None

        return SuggestedUserFilterSettings(text=text_val, salary=salary_val, currency=currency_val)

