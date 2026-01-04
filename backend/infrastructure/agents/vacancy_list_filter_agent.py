from __future__ import annotations

import json
from typing import List, Sequence

from openai import AsyncOpenAI
from loguru import logger

from config import OpenAIConfig
from domain.entities.filtered_vacancy_list import FilteredVacancyListDto
from domain.entities.vacancy_list import VacancyListItem
from domain.interfaces.vacancy_list_filter_service_port import VacancyListFilterServicePort
from infrastructure.agents.base_agent import BaseAgent


class VacancyListFilterAgent(BaseAgent, VacancyListFilterServicePort):
    """LLM‑агент для фильтрации list-вакансий по резюме.

    Инкапсулирует промпты и работу с AsyncOpenAI.
    """

    AGENT_NAME = "VacancyListFilterAgent"

    async def filter_vacancy_list(
        self,
        vacancies: List[VacancyListItem],
        resume: str,
        user_filter_params: str | None = None,
    ) -> List[FilteredVacancyListDto]:
        if not vacancies:
            return []

        prompt = self._build_prompt(vacancies, resume, user_filter_params)
        logger.info(
            f"[{self.AGENT_NAME}] filtering {len(vacancies)} list vacancies model={self._config.model}"
        )

        messages = [
            {
                "role": "system",
                "content": """Ты ассистент по оценке релевантности вакансий конкретному кандидату.

Тебе в сообщении пользователя даны:
- текст резюме кандидата;
- несколько вакансий с названием, компанией, зарплатой, графиком, требованиями и обязанностями (краткая информация из списка);
- дополнительные требования к фильтрации (если указаны пользователем).

Твоя задача — для КАЖДОЙ вакансии оценить, насколько она подходит именно этому кандидату,
исходя из резюме и дополнительных требований. Оценивай по следующим принципам:

1. Основной критерий — совпадение роли и содержания обязанностей с опытом и интересами кандидата,
   которые описаны в резюме.
2. Важно учитывать:
   - совпадение обязанностей и задач с тем, что кандидат делал раньше;
   - совпадение требуемых навыков и технологий с тем, что указано в резюме;
   - уровень (junior/middle/senior/lead и т.п.) и сложность задач;
   - домен/область (если в резюме явно есть предпочтения или сильный опыт в определённой области);
   - формат работы: ВАЖНО! Если вакансия имеет формат "Удалённо" или "Гибрид", а кандидат в резюме указал,
     что готов к удалённой работе, то локация (город) НЕ должна снижать оценку. Если вакансия удалённая,
     кандидат может работать из любого города. Если вакансия только офисная, а кандидат указал только
     удалёнку, это может снижать оценку.
3. Если пользователь указал дополнительные требования к фильтрации, ОБЯЗАТЕЛЬНО учитывай их при оценке.
   Вакансии, не соответствующие дополнительным требованиям, должны получать более низкую оценку confidence.
4. Если роль и обязанности сильно отличаются от профиля кандидата, ставь низкую оценку
   даже при частичном совпадении по технологиям.
5. Шкала:
   - 0.7–1.0 — вакансия очень хорошо соответствует опыту и ожидаемой роли кандидата;
   - 0.4–0.7 — частичное совпадение: что‑то подходит, но есть серьёзные отличия (роль, задачи, стек, уровень);
   - 0.0–0.4 — вакансия в целом не для этого кандидата (другая роль/функция/уровень/направление).

Оценивай каждую вакансию независимо от других.

Верни строго JSON-массив объектов вида:
[
  {"vacancy_id": 123, "confidence": 0.85, "reason": "Хорошее совпадение по стеку и опыту"},
  {"vacancy_id": 456, "confidence": 0.2, "reason": "Другая роль, не подходит"}
]
где:
- vacancy_id — целочисленный идентификатор вакансии;
- confidence — число с плавающей точкой от 0 до 1;
- reason — короткая причина оценки (1-2 предложения, максимум 100 символов).

ФОРМАТ ТИПОГРАФИКИ:
- В значениях поля reason НЕ используй длинное тире (символ '—').
- Если нужно тире, используй только обычный дефис '-'.

Никакого другого текста, комментариев или форматирования, только JSON-массив.""",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        def parse_func(content: str) -> List[FilteredVacancyListDto]:
            return self._parse_response(content, vacancies)

        def validate_func(result: List[FilteredVacancyListDto]) -> bool:
            return not result

        return await self._call_llm_with_retry(
            messages=messages,
            parse_func=parse_func,
            validate_func=validate_func,
        )

    def _build_prompt(
        self,
        vacancies: Sequence[VacancyListItem],
        resume: str,
        user_filter_params: str | None = None,
    ) -> str:
        """Формируем текстовый промпт с резюме и краткой инфой по list-вакансиям."""

        lines: list[str] = []
        lines.append("РЕЗЮМЕ КАНДИДАТА:")
        lines.append(resume.strip())
        lines.append("")

        # Добавляем пользовательские требования, если они есть
        if user_filter_params and user_filter_params.strip():
            lines.append("ДОПОЛНИТЕЛЬНЫЕ ТРЕБОВАНИЯ К ФИЛЬТРАЦИИ:")
            lines.append(user_filter_params.strip())
            lines.append("")
            lines.append(
                "ВАЖНО: Учитывай эти требования при оценке вакансий. "
                "Если вакансия не соответствует дополнительным требованиям, "
                "снижай оценку confidence."
            )
            lines.append("")

        lines.append("СПИСОК ВАКАНСИЙ:")
        for v in vacancies:
            lines.append(f"- id={v.vacancy_id}")
            lines.append(f"  Название: {v.name}")
            if v.company_name:
                lines.append(f"  Компания: {v.company_name}")
            if v.area_name:
                lines.append(f"  Город: {v.area_name}")
            if v.address_city:
                lines.append(f"  Адрес (город): {v.address_city}")
            if v.address_street:
                lines.append(f"  Адрес (улица): {v.address_street}")
            
            # Зарплата
            salary_parts = []
            if v.salary_from is not None:
                salary_parts.append(f"от {v.salary_from}")
            if v.salary_to is not None:
                salary_parts.append(f"до {v.salary_to}")
            if v.salary_currency:
                salary_parts.append(v.salary_currency)
            if salary_parts:
                salary_str = " ".join(salary_parts)
                if v.salary_gross is not None:
                    salary_str += " (gross)" if v.salary_gross else " (net)"
                lines.append(f"  Зарплата: {salary_str}")
            
            if v.schedule_name:
                lines.append(f"  График работы: {v.schedule_name}")
            if v.professional_roles:
                lines.append("  Профессиональные роли: " + ", ".join(v.professional_roles))
            if v.snippet_requirement:
                lines.append(f"  Требования: {v.snippet_requirement}")
            if v.snippet_responsibility:
                lines.append(f"  Обязанности: {v.snippet_responsibility}")
            if v.vacancy_type_name:
                lines.append(f"  Тип вакансии: {v.vacancy_type_name}")
            lines.append("")

        lines.append(
            "Для каждой вакансии верни JSON-объект с полями 'vacancy_id', 'confidence' (0..1) и 'reason', "
            "где confidence — твоя оценка соответствия этой вакансии данному резюме, "
            "а reason — короткая причина оценки (1-2 предложения, максимум 100 символов)."
        )
        lines.append(
            "Ответ должен быть строго JSON-массивом, например: "
            "[{\"vacancy_id\": 123, \"confidence\": 0.8, \"reason\": \"Совпадение по стеку\"}, "
            "{\"vacancy_id\": 456, \"confidence\": 0.4, \"reason\": \"Другая роль\"}]"
        )

        return "\n".join(lines)

    def _parse_response(
        self,
        content: str,
        vacancies: Sequence[VacancyListItem],
    ) -> List[FilteredVacancyListDto]:
        """Разбор JSON-ответа модели в список DTO."""

        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            logger.error(f"[ai] не удалось распарсить JSON от модели: {exc}")
            return []

        if not isinstance(data, list):
            logger.warning("[ai] ответ модели не является списком")
            return []

        # Список id вакансий из текущего батча для валидации
        allowed_ids = {v.vacancy_id for v in vacancies}

        result: list[FilteredVacancyListDto] = []
        for item in data:
            if not isinstance(item, dict):
                continue

            vacancy_id = item.get("vacancy_id")
            confidence = item.get("confidence")
            reason = item.get("reason")

            try:
                vacancy_id_int = int(vacancy_id)
            except (TypeError, ValueError):
                continue

            if vacancy_id_int not in allowed_ids:
                continue

            try:
                conf_float = float(confidence)
            except (TypeError, ValueError):
                continue

            # clamp к [0.0, 1.0]
            if conf_float < 0.0:
                conf_float = 0.0
            elif conf_float > 1.0:
                conf_float = 1.0

            # Обработка reason: обрезаем до 100 символов, если слишком длинный
            reason_str: str | None = None
            if reason is not None:
                if isinstance(reason, str):
                    reason_str = reason[:100] if len(reason) > 100 else reason
                else:
                    reason_str = str(reason)[:100]

            result.append(
                FilteredVacancyListDto(
                    vacancy_id=vacancy_id_int, confidence=conf_float, reason=reason_str
                )
            )

        return result

