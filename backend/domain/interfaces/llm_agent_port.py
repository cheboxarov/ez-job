"""Базовый порт для LLM агентов."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from domain.entities.resume import Resume
from domain.entities.vacancy_detail import VacancyDetail


class LLMAgentPort(ABC):
    """Базовый порт для LLM агентов.
    
    Инфраструктура должна реализовать этот интерфейс.
    """

    @abstractmethod
    async def execute(self, prompt: str, **kwargs) -> Any:
        """Выполнить запрос к LLM.
        
        Args:
            prompt: Промпт для LLM.
            **kwargs: Дополнительные параметры.
        
        Returns:
            Результат выполнения запроса.
        """
        pass


class CoverLetterGeneratorPort(LLMAgentPort):
    """Порт для генерации сопроводительных писем.
    
    Наследует от LLMAgentPort для единообразия интерфейсов.
    """

    @abstractmethod
    async def generate(
        self,
        resume: Resume | str,
        vacancy: VacancyDetail | str,
        user_params: str | None = None,
        user_id: UUID | None = None,
    ) -> str:
        """Сгенерировать сопроводительное письмо.
        
        Args:
            resume: Резюме кандидата (сущность или текст).
            vacancy: Вакансия (сущность или описание).
            user_params: Дополнительные требования пользователя.
            user_id: UUID пользователя.
        
        Returns:
            Текст сопроводительного письма.
        """
        pass


class ResumeEvaluatorPort(LLMAgentPort):
    """Порт для оценки резюме.
    
    Наследует от LLMAgentPort для единообразия интерфейсов.
    """

    @abstractmethod
    async def evaluate(
        self,
        resume: Resume | str,
        vacancy: VacancyDetail | None = None,
        user_id: UUID | None = None,
    ) -> dict[str, Any]:
        """Оценить резюме.
        
        Args:
            resume: Резюме для оценки (сущность или текст).
            vacancy: Вакансия для контекста (опционально).
            user_id: UUID пользователя.
        
        Returns:
            Словарь с оценкой (conf, remarks, summary).
        """
        pass
