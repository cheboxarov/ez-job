"""Агент для генерации сопроводительных писем на основе текстового описания вакансии."""

from __future__ import annotations

import re

from openai import AsyncOpenAI

from config import OpenAIConfig
from domain.interfaces.cover_letter_generator_port import CoverLetterGeneratorPort


class CoverLetterGeneratorAgent(CoverLetterGeneratorPort):
    """LLM‑агент для генерации сопроводительного письма к вакансии.

    Работает с текстовым описанием вакансии (для list-вакансий),
    в отличие от CoverLetterAgent, который работает с FilteredVacancyDetail.
    """

    def __init__(
        self,
        config: OpenAIConfig,
        client: AsyncOpenAI | None = None,
    ) -> None:
        self._config = config
        if client is None:
            api_key = self._config.api_key
            if not api_key:
                raise RuntimeError("OpenAIConfig.api_key не задан (проверь конфиг/окружение)")
            client = AsyncOpenAI(
                base_url=self._config.base_url,
                api_key=api_key,
            )
        self._client = client

    async def generate(self, resume: str, vacancy_description: str) -> str:
        """Сгенерировать сопроводительное письмо для вакансии.

        Args:
            resume: Текст резюме кандидата.
            vacancy_description: Описание вакансии (название, требования, обязанности).

        Returns:
            Текст сопроводительного письма на русском языке.
        """
        if not resume or not vacancy_description:
            return ""

        try:
            prompt = self._build_prompt(resume, vacancy_description)
            print(
                f"[ai] генерирую сопроводительное письмо model={self._config.model}",
                flush=True,
            )

            response = await self._client.chat.completions.create(
                model=self._config.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Ты профессиональный HR-консультант, специализирующийся на написании кратких и убедительных сопроводительных писем.

Твоя задача — написать КОРОТКОЕ (100-150 слов) персонализированное сопроводительное письмо на русском языке.

СТРУКТУРА (все в одном абзаце):
1. Краткое приветствие с упоминанием вакансии
2. Перечисление ключевых технологий из вакансии, с которыми кандидат работал (ОБЯЗАТЕЛЬНО!)
3. Один конкретный пример релевантного опыта из резюме
4. Краткое выражение желания работать в компании

КРИТИЧЕСКИ ВАЖНО:

1. СООТВЕТСТВИЕ СТЕКУ:
   - ОБЯЗАТЕЛЬНО перечисли 3-5 конкретных технологий из вакансии: "Работал с вашим стеком: Python, FastAPI, PostgreSQL, Redis"
   - Сопоставь требования вакансии с опытом из резюме

2. КРАТКОСТЬ И КОНКРЕТНОСТЬ:
   - Один абзац, без лишних слов
   - Один конкретный пример из резюме (проект/задача), релевантный вакансии
   - Избегай общих фраз и "воды"

3. МОТИВАЦИЯ:
   - Кратко вырази желание: "Очень хочу работать в вашей компании" или "Мне интересна эта позиция"

Пример хорошего краткого письма:
"Добрый день! Откликаюсь на вакансию Python-разработчика. Работал с вашим стеком: Python, FastAPI, PostgreSQL, Redis — это именно те технологии, с которыми я работаю ежедневно. Разрабатывал микросервисную архитектуру для real-time транскрипции встреч с использованием LiveKit и WebRTC. Мой опыт полностью соответствует требованиям. Очень хочу работать в вашей компании и готов быстро влиться в команду."

Важно:
- Длина: 100-150 слов (один абзац)
- Конкретные технологии из вакансии
- Один релевантный пример из резюме
- Уверенный тон, без неуверенности

Верни ТОЛЬКО текст письма, без markdown-разметки, без заголовков, без подписей. Начни сразу с обращения.""",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.7,
            )

            content = response.choices[0].message.content if response.choices else None
            if not content:
                print("[ai] пустой ответ от модели при генерации письма", flush=True)
                return ""

            # Очищаем возможные markdown-артефакты
            cover_letter = content.strip()
            # Убираем markdown-код блоки, если они есть
            if cover_letter.startswith("```"):
                lines = cover_letter.split("\n")
                # Пропускаем первую строку (```) и последнюю (```)
                cover_letter = "\n".join(lines[1:-1]).strip()

            return cover_letter
        except Exception as exc:
            print(f"[ai] ошибка при генерации сопроводительного письма: {exc}", flush=True)
            return ""

    def _build_prompt(self, resume: str, vacancy_description: str) -> str:
        """Формирует текстовый промпт с информацией о вакансии и резюме."""

        lines: list[str] = []
        lines.append("РЕЗЮМЕ КАНДИДАТА:")
        lines.append(resume.strip())
        lines.append("")
        lines.append("ВАКАНСИЯ:")
        lines.append(vacancy_description.strip())
        lines.append("")
        lines.append(
            "Напиши КОРОТКОЕ сопроводительное письмо (100-150 слов, один абзац) для этой вакансии. "
            "ОБЯЗАТЕЛЬНО:"
        )
        lines.append(
            "1. Перечисли 3-5 конкретных технологий из вакансии, с которыми кандидат работал "
            "(формат: 'Работал с вашим стеком: Python, FastAPI, PostgreSQL')"
        )
        lines.append(
            "2. Приведи ОДИН конкретный пример проекта/задачи из резюме, релевантный вакансии"
        )
        lines.append(
            "3. Кратко вырази желание работать ('Очень хочу работать в вашей компании')"
        )
        lines.append(
            "4. Письмо должно быть одним абзацем, без лишних слов, убедительным и конкретным"
        )

        return "\n".join(lines)
