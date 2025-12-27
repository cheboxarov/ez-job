from __future__ import annotations

import re

from openai import AsyncOpenAI

from config import OpenAIConfig
from domain.entities.filtered_vacancy import FilteredVacancyDetail
from domain.interfaces.cover_letter_service_port import CoverLetterServicePort


class CoverLetterAgent(CoverLetterServicePort):
    """LLM‑агент для генерации сопроводительного письма к вакансии.

    Инкапсулирует промпты и работу с AsyncOpenAI для создания
    персонализированного сопроводительного письма на основе резюме и вакансии.
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

    async def generate(
        self,
        vacancy: FilteredVacancyDetail,
        resume: str,
    ) -> str:
        """Генерирует сопроводительное письмо для указанной вакансии.

        Args:
            vacancy: Детальная информация о вакансии с оценкой релевантности.
            resume: Текст резюме кандидата.

        Returns:
            Текст сопроводительного письма на русском языке.
        """
        if not vacancy or not resume:
            return ""

        try:
            prompt = self._build_prompt(vacancy, resume)
            print(
                f"[ai] генерирую сопроводительное письмо для вакансии {vacancy.vacancy_id} "
                f"model={self._config.model}",
                flush=True,
            )

            response = await self._client.chat.completions.create(
                model=self._config.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Ты профессиональный HR-консультант и копирайтер, специализирующийся на написании убедительных сопроводительных писем.

Твоя задача — написать персонализированное сопроводительное письмо на русском языке, которое активно "продает" кандидата.

СТРУКТУРА ПИСЬМА:
1. Вступление с упоминанием вакансии
2. Блок о совпадении стека технологий (ОБЯЗАТЕЛЬНО!)
3. Релевантный опыт из резюме
4. Выражение желания работать в компании
5. Заключение

КРИТИЧЕСКИ ВАЖНО:

1. СООТВЕТСТВИЕ СТЕКУ ТЕХНОЛОГИЙ:
   - ОБЯЗАТЕЛЬНО перечисли конкретные технологии из вакансии, с которыми кандидат работал
   - Используй формулировки: "Я работал с вашим стеком [перечисли технологии]", "Мой опыт включает [технологии из вакансии]", "Я знаком с технологиями [список]"
   - Прямо сопоставь требования вакансии с опытом из резюме
   - Пример: "Я работал с вашим стеком: Python, FastAPI, PostgreSQL, Redis — это именно те технологии, с которыми я работаю ежедневно"

2. ПОДЧЕРКИВАНИЕ СООТВЕТСТВИЯ:
   - Явно укажи: "Я вам подхожу", "Мой опыт соответствует требованиям", "Я идеально подхожу для этой позиции"
   - Приведи 2-3 конкретных примера проектов/задач из резюме, которые релевантны вакансии

3. МОТИВАЦИЯ И ЖЕЛАНИЕ РАБОТАТЬ:
   - ОБЯЗАТЕЛЬНО вырази сильное желание работать именно в этой компании
   - Используй фразы: "Очень хочу работать в вашей компании", "Эта вакансия идеально соответствует моим интересам", "Мне очень интересна эта позиция"
   - Объясни, почему именно эта позиция привлекательна

4. УВЕРЕННЫЙ ТОН:
   - Используй активные формулировки: "Я готов внести вклад", "Мой опыт позволит мне быстро влиться в команду"
   - Избегай неуверенности и общих фраз

Важно:
- Используй конкретные примеры из резюме, которые соответствуют требованиям вакансии
- Письмо должно быть убедительным и продающим
- Длина: примерно 250-350 слов

ФОРМАТ ТИПОГРАФИКИ:
- НЕ используй длинное тире (символ '—') ни в одном месте текста.
- Если нужно тире, используй только обычный дефис '-'.

Верни ТОЛЬКО текст письма, без markdown-разметки, без заголовков типа "Сопроводительное письмо", без подписей. Начни сразу с обращения (например, "Здравствуйте," или "Добрый день,").""",
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
        except Exception as exc:  # pragma: no cover - диагностический путь
            print(f"[ai] ошибка при генерации сопроводительного письма: {exc}", flush=True)
            return ""

    def _build_prompt(
        self,
        vacancy: FilteredVacancyDetail,
        resume: str,
    ) -> str:
        """Формирует текстовый промпт с информацией о вакансии и резюме."""

        lines: list[str] = []
        lines.append("РЕЗЮМЕ КАНДИДАТА:")
        lines.append(resume.strip())
        lines.append("")
        lines.append("ВАКАНСИЯ:")
        lines.append(f"Название: {vacancy.name}")
        if vacancy.company_name:
            lines.append(f"Компания: {vacancy.company_name}")
        if vacancy.area_name:
            lines.append(f"Город: {vacancy.area_name}")
        if vacancy.compensation:
            lines.append(f"Зарплата: {vacancy.compensation}")
        if vacancy.work_experience:
            lines.append(f"Требуемый опыт: {vacancy.work_experience}")
        if vacancy.employment:
            lines.append(f"Тип занятости: {vacancy.employment}")
        if vacancy.work_formats:
            lines.append("Формат работы: " + ", ".join(vacancy.work_formats))
        if vacancy.key_skills:
            lines.append("Ключевые навыки: " + ", ".join(vacancy.key_skills))
        if vacancy.description_html:
            # Упрощаем HTML-описание, убирая теги для лучшей читаемости промпта
            description_text = re.sub(r"<[^>]+>", " ", vacancy.description_html)
            description_text = re.sub(r"\s+", " ", description_text).strip()
            if description_text:
                lines.append("")
                lines.append("Описание вакансии:")
                lines.append(description_text[:2000])  # Ограничиваем длину

        lines.append("")
        lines.append(
            "Напиши сопроводительное письмо для этой вакансии на основе резюме кандидата. "
            "ОБЯЗАТЕЛЬНО:"
        )
        lines.append(
            "1. Перечисли конкретные технологии из вакансии, с которыми кандидат работал "
            "(используй формулировки 'Я работал с вашим стеком', 'Мой опыт включает')"
        )
        lines.append(
            "2. Подчеркни соответствие кандидата требованиям ('Я вам подхожу', 'Мой опыт соответствует')"
        )
        lines.append(
            "3. Вырази сильное желание работать в этой компании ('Очень хочу работать у вас', "
            "'Мне очень интересна эта позиция')"
        )
        lines.append(
            "4. Приведи конкретные примеры из резюме, релевантные вакансии"
        )

        return "\n".join(lines)
