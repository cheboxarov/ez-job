"""Интерфейс репозитория откликов на вакансии."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from domain.entities.vacancy_response import VacancyResponse


class VacancyResponseRepositoryPort(ABC):
    """Интерфейс репозитория откликов на вакансии."""

    @abstractmethod
    async def create(self, vacancy_response: VacancyResponse) -> VacancyResponse:
        """Создать отклик на вакансию."""

    @abstractmethod
    async def get_by_resume_id_with_pagination(
        self, resume_id: UUID, offset: int, limit: int
    ) -> tuple[list[VacancyResponse], int]:
        """Получить отклики по resume_id с пагинацией."""

    @abstractmethod
    async def get_by_resume_hash_with_pagination(
        self, resume_hash: str, offset: int, limit: int
    ) -> tuple[list[VacancyResponse], int]:
        """Получить отклики по resume_hash с пагинацией."""

    @abstractmethod
    async def get_responses_count_by_date_range(
        self, user_id: UUID, start_date: date, end_date: date
    ) -> list[tuple[date, int]]:
        """Получить количество откликов по дням за указанный период.
        
        Args:
            user_id: UUID пользователя.
            start_date: Начальная дата (включительно).
            end_date: Конечная дата (включительно).
            
        Returns:
            Список кортежей (дата, количество откликов) для каждого дня в диапазоне.
        """
