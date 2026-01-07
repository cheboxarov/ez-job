"""Интерфейс для агента генерации ответов на тест вакансии."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List
from uuid import UUID

from domain.entities.vacancy_test import VacancyTest


class VacancyTestAgentServicePort(ABC):
    """Порт сервиса агента для генерации ответов на тест вакансии.

    Инфраструктура должна реализовать этот интерфейс.
    """

    @abstractmethod
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
        raise NotImplementedError

