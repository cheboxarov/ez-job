"""Use case для генерации ответов на тест вакансии."""

from __future__ import annotations

from typing import Dict, List
from uuid import UUID

from loguru import logger

from domain.entities.vacancy_test import VacancyTest
from domain.interfaces.vacancy_test_agent_service_port import VacancyTestAgentServicePort
from domain.exceptions.agent_exceptions import AgentParseError


class GenerateTestAnswersUseCase:
    """Use case для генерации ответов на тест вакансии с помощью LLM-агента.

    Использует резюме кандидата для генерации релевантных ответов на вопросы теста.
    """

    def __init__(
        self,
        vacancy_test_agent: VacancyTestAgentServicePort,
    ) -> None:
        """Инициализация use case.

        Args:
            vacancy_test_agent: Агент для генерации ответов на тест.
        """
        self._vacancy_test_agent = vacancy_test_agent

    def set_unit_of_work(self, unit_of_work) -> None:
        """Обновить UnitOfWork в агенте для логирования вызовов LLM.

        Args:
            unit_of_work: Новый UnitOfWork для логирования (может быть None).
        """
        self._vacancy_test_agent.set_unit_of_work(unit_of_work)

    async def execute(
        self,
        test: VacancyTest,
        resume: str,
        user_params: str | None = None,
        user_id: UUID | None = None,
    ) -> Dict[str, str | List[str]]:
        """Сгенерировать ответы на вопросы теста.

        Args:
            test: Тест вакансии с вопросами.
            resume: Текст резюме кандидата для контекста.
            user_params: Дополнительные требования/предпочтения пользователя (опционально).

        Returns:
            Словарь, где ключ - field_name вопроса, значение - текст ответа (для text/select) или список значений (для multiselect).
            Возвращает пустой словарь при ошибках.
        """
        if not test or not test.questions:
            logger.warning("Тест пуст или не содержит вопросов")
            return {}

        if not resume or not resume.strip():
            logger.warning("Резюме пусто, невозможно сгенерировать ответы")
            return {}

        try:
            test_answers = await self._vacancy_test_agent.generate_test_answers(
                test=test,
                resume=resume,
                user_params=user_params,
                user_id=user_id,
            )
            
            if not test_answers:
                logger.warning(
                    f"Не удалось сгенерировать ответы на тест с {len(test.questions)} вопросами"
                )
                return {}
            
            logger.info(
                f"Сгенерированы ответы на {len(test_answers)} вопросов из {len(test.questions)}"
            )
            return test_answers
        except AgentParseError as exc:
            logger.error(
                f"Ошибка парсинга ответа агента при генерации ответов на тест: {exc}",
                exc_info=True,
            )
            return {}
        except Exception as exc:
            logger.error(
                f"Ошибка при генерации ответов на тест: {exc}",
                exc_info=True,
            )
            return {}

