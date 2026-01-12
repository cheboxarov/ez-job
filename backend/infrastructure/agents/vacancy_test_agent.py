"""LLM-агент для генерации ответов на тест вакансии."""

from __future__ import annotations

import json
from typing import Dict, List
from uuid import UUID

from openai import AsyncOpenAI
from loguru import logger

from config import OpenAIConfig
from domain.entities.vacancy_test import VacancyTest
from domain.interfaces.vacancy_test_agent_service_port import VacancyTestAgentServicePort
from infrastructure.agents.base_agent import BaseAgent


class VacancyTestAgent(BaseAgent, VacancyTestAgentServicePort):
    """LLM-агент для генерации ответов на тест вакансии.

    Инкапсулирует промпты и работу с AsyncOpenAI для создания ответов
    на вопросы теста вакансии на основе резюме кандидата.
    """

    AGENT_NAME = "VacancyTestAgent"

    async def generate_test_answers(
        self,
        test: VacancyTest,
        resume: str,
        user_params: str | None = None,
        user_id: UUID | None = None,
    ) -> Dict[str, str | List[str]]:
        """Генерирует ответы на вопросы теста вакансии на основе резюме кандидата.

        Args:
            test: Тест вакансии с вопросами.
            resume: Текст резюме кандидата для контекста при генерации ответов.
            user_params: Дополнительные требования/предпочтения пользователя (опционально).

        Returns:
            Словарь, где ключ - field_name вопроса (например, "task_291683492_text"),
            значение - текст ответа (для text/select) или список значений (для multiselect).
        """
        if not test or not test.questions or not resume:
            return {}

        prompt = self._build_prompt(test, resume, user_params)
        logger.info(
            f"[{self.AGENT_NAME}] генерирую ответы на тест вакансии ({len(test.questions)} вопросов) "
            f"model={self._config.get_model_for_agent(self.AGENT_NAME)}"
        )

        messages = [
            {
                "role": "system",
                "content": """Ты ассистент, который помогает кандидатам отвечать на вопросы тестов при отклике на вакансии.

Твоя задача — сгенерировать ответы на вопросы теста вакансии так, как бы ответил сам кандидат от первого лица, естественно и просто.

ТИПЫ ВОПРОСОВ:
1. Текстовые вопросы (field_name содержит "_text"): нужно сгенерировать текстовый ответ (1-2 предложения)
2. Select вопросы (field_name БЕЗ "_text", тип "select"): нужно выбрать один из предложенных вариантов ответа и вернуть его value (ID варианта) как строку
3. Multiselect вопросы (field_name БЕЗ "_text", тип "multiselect"): нужно выбрать один или несколько вариантов ответа и вернуть массив их values (ID вариантов) как JSON массив строк

СТИЛЬ ОТВЕТОВ - КАК ЖИВОЙ ЧЕЛОВЕК:
1. Отвечай от первого лица: "Я работал...", "У меня есть опыт...", "Мне интересно..."
2. Пиши просто и естественно, как в обычном разговоре
3. НЕ упоминай названия компаний напрямую - говори об опыте без конкретных брендов
4. НЕ перечисляй технологии списком - упоминай только если вопрос об этом напрямую
5. Будь кратким: для вопросов о зарплате просто укажи сумму, для простых вопросов - 1 предложение
6. Будь честным, но не перегружай деталями

ФОРМАТ ТИПОГРАФИКИ:
- НЕ используй длинное тире (символ '—') ни в одном ответе.
- Если нужно тире, используй только обычный дефис '-'.

ПРИМЕРЫ:
Плохо: "Мои зарплатные ожидания составляют 250 000 рублей netto в месяц при условии полностью удаленной работы без гибридного формата. Эта сумма соответствует моему опыту tech-lead'а в разработке микросервисных backend-систем на Python (FastAPI, Django), интеграциях AI/LLM и эксплуатации в Kubernetes, накопленному за более чем 3 года в FlowAI и ТеМа."

Хорошо: "250 000 рублей netto. Рассматриваю только удаленку."

Плохо: "Я работал в компании FlowAI над проектом @node, где использовал FastAPI, Django и Kubernetes."

Хорошо: "У меня опыт разработки backend-систем на Python, работал с микросервисами и облачной инфраструктурой."

Верни строго JSON-объект, где ключи — это field_name вопросов.

Примеры формата ответа:
{
  "task_291683492_text": "Я работал с Python около 4 лет, есть опыт в backend-разработке",
  "task_296586238": "296586239",
  "task_316925806": ["316925807", "316925808"]
}

Никакого другого текста, комментариев или форматирования, только JSON-объект.""",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        def parse_func(content: str) -> Dict[str, str | List[str]]:
            return self._parse_response(content, test)

        def validate_func(result: Dict[str, str | List[str]]) -> bool:
            return not result

        # Формируем контекст для логирования
        context = {
            "use_case": "generate_test_answers",
            "vacancy_id": test.vacancy_id if hasattr(test, "vacancy_id") else None,
            "question_count": len(test.questions) if test.questions else 0,
        }

        return await self._call_llm_with_retry(
            messages=messages,
            parse_func=parse_func,
            validate_func=validate_func,
            user_id=user_id,
            context=context,
        )

    def _build_prompt(
        self,
        test: VacancyTest,
        resume: str,
        user_params: str | None = None,
    ) -> str:
        """Формирует текстовый промпт с информацией о тесте и резюме.

        Args:
            test: Тест вакансии с вопросами.
            resume: Текст резюме кандидата.
            user_params: Дополнительные требования/предпочтения пользователя (опционально).

        Returns:
            Текст промпта для передачи в LLM.
        """
        lines: list[str] = []

        # Добавляем описание теста, если есть
        if test.description:
            lines.append("ОПИСАНИЕ ТЕСТА:")
            lines.append(test.description.strip())
            lines.append("")

        # Добавляем резюме
        lines.append("РЕЗЮМЕ КАНДИДАТА:")
        lines.append(resume.strip())
        lines.append("")
        
        # Добавляем дополнительные требования пользователя, если есть
        if user_params and user_params.strip():
            lines.append("ДОПОЛНИТЕЛЬНЫЕ ТРЕБОВАНИЯ/ПРЕДПОЧТЕНИЯ:")
            lines.append(user_params.strip())
            lines.append("")
            lines.append(
                "Учитывай эти требования при генерации ответов на вопросы теста."
            )
            lines.append("")

        # Добавляем список вопросов
        lines.append("ВОПРОСЫ ТЕСТА:")
        for question in test.questions:
            lines.append(f"- field_name: {question.field_name}")
            lines.append(f"  Тип: {question.question_type}")
            lines.append(f"  Вопрос: {question.question_text}")
            
            if question.question_type in ("select", "multiselect") and question.options:
                lines.append("  Варианты ответов:")
                for option in question.options:
                    lines.append(f"    - value: {option.value}, текст: {option.text}")
            
            lines.append("")

        lines.append(
            "Сгенерируй ответы на каждый вопрос так, как бы ответил сам кандидат - просто, естественно, от первого лица. "
            "Избегай формальностей, не упоминай названия компаний, будь кратким. "
            "Для вопросов о зарплате - просто укажи сумму без объяснений."
        )
        lines.append("")
        lines.append(
            "ВАЖНО: "
            "Для текстовых вопросов (field_name содержит '_text') верни короткий ответ от первого лица (1-2 предложения). "
            "Для select вопросов (тип 'select') выбери наиболее подходящий вариант и верни его value (ID) как строку. "
            "Для multiselect вопросов (тип 'multiselect') выбери один или несколько подходящих вариантов и верни массив их values (ID) как JSON массив строк."
        )
        lines.append("")
        lines.append(
            "Верни JSON-объект, где ключи — это field_name вопросов."
        )

        return "\n".join(lines)

    def _parse_response(
        self,
        content: str,
        test: VacancyTest,
    ) -> Dict[str, str]:
        """Разбирает JSON-ответ модели в словарь ответов.

        Args:
            content: Содержимое ответа от LLM.
            test: Тест вакансии для валидации field_name.

        Returns:
            Словарь, где ключ - field_name, значение - ответ.
        """
        # Пытаемся извлечь JSON из markdown кода, если он обернут
        content_cleaned = content.strip()
        if content_cleaned.startswith("```"):
            lines = content_cleaned.split("\n")
            # Пропускаем первую строку (```json или ```) и последнюю (```)
            if len(lines) > 2:
                content_cleaned = "\n".join(lines[1:-1]).strip()

        try:
            data = json.loads(content_cleaned)
        except json.JSONDecodeError as exc:
            logger.error(f"[ai] не удалось распарсить JSON от модели: {exc}")
            logger.debug(f"[ai] content: {content_cleaned[:500]}")
            return {}

        if not isinstance(data, dict):
            logger.warning("[ai] ответ модели не является объектом (dict)")
            return {}

        # Валидируем field_name - должны соответствовать вопросам из теста
        allowed_field_names = {q.field_name for q in test.questions}
        question_map = {q.field_name: q for q in test.questions}

        result: Dict[str, str | List[str]] = {}
        for field_name, answer in data.items():
            if field_name not in allowed_field_names:
                logger.warning(f"[ai] неизвестный field_name в ответе: {field_name}")
                continue

            question = question_map.get(field_name)
            if not question:
                continue

            # Для multiselect вопросов ожидается массив значений
            if question.question_type == "multiselect":
                if not isinstance(answer, list):
                    # Если не массив, пытаемся преобразовать или создаем пустой массив
                    logger.warning(
                        f"[ai] для multiselect вопроса {field_name} ожидался массив, получен {type(answer)}"
                    )
                    if isinstance(answer, str):
                        # Может быть JSON строка
                        try:
                            answer = json.loads(answer)
                            if not isinstance(answer, list):
                                answer = []
                        except Exception as exc:
                            logger.warning(
                                f"Не удалось распарсить JSON ответ на тест вакансии: "
                                f"answer={answer}, error={exc}"
                            )
                            answer = []
                    else:
                        answer = []
                
                # Валидируем значения в списке
                if question.options and answer:
                    allowed_values = {opt.value for opt in question.options}
                    validated_values = [v for v in answer if str(v) in allowed_values]
                    if not validated_values:
                        logger.warning(
                            f"[ai] для multiselect вопроса {field_name} ни одно значение не соответствует "
                            f"допустимым вариантам {allowed_values}, выбираю первый вариант"
                        )
                        validated_values = [question.options[0].value] if question.options else []
                    answer = [str(v) for v in validated_values]
                else:
                    answer = [str(v) for v in answer] if answer else []
                
                result[field_name] = answer
                
            elif question.question_type == "select":
                # Для select вопросов - одно значение
                if not isinstance(answer, str):
                    answer = str(answer)
                
                if question.options:
                    allowed_values = {opt.value for opt in question.options}
                    if answer not in allowed_values:
                        logger.warning(
                            f"[ai] для select вопроса {field_name} значение {answer} не соответствует "
                            f"допустимым вариантам {allowed_values}, выбираю первый вариант"
                        )
                        answer = question.options[0].value
                
                result[field_name] = answer
            else:
                # Для текстовых вопросов
                if not isinstance(answer, str):
                    answer = str(answer)
                
                # Обрезаем слишком длинные ответы
                if len(answer) > 2000:
                    answer = answer[:2000]
                    logger.debug(f"[ai] обрезан ответ для {field_name} до 2000 символов")
                
                result[field_name] = answer.strip()

        return result

