"""Интерфейс репозитория откликов на вакансии."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime
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

    @abstractmethod
    async def get_metrics_by_period(
        self,
        *,
        start_date: datetime,
        end_date: datetime,
        plan_id: UUID | None = None,
        time_step: str = "day",
    ) -> list[tuple[datetime, int, int]]:
        """Получить метрики откликов по периоду с группировкой по времени.

        Args:
            start_date: Начальная дата (включительно).
            end_date: Конечная дата (включительно).
            plan_id: Фильтр по ID плана подписки (опционально).
            time_step: Шаг группировки ('day', 'week', 'month').

        Returns:
            Список кортежей (дата/время начала периода, количество откликов,
            количество уникальных пользователей).
        """

    @abstractmethod
    async def get_total_metrics(
        self,
        *,
        start_date: datetime,
        end_date: datetime,
        plan_id: UUID | None = None,
    ) -> tuple[int, int, float]:
        """Получить суммарные метрики откликов за период.

        Args:
            start_date: Начальная дата (включительно).
            end_date: Конечная дата (включительно).
            plan_id: Фильтр по ID плана подписки (опционально).

        Returns:
            Кортеж (общее количество откликов, количество уникальных пользователей,
            средние отклики на пользователя).
        """

    @abstractmethod
    async def get_failed_by_resume_and_vacancy_id(
        self, resume_id: UUID, vacancy_id: int
    ) -> VacancyResponse | None:
        """Получить неудачный отклик по resume_id и vacancy_id.

        Args:
            resume_id: UUID резюме.
            vacancy_id: ID вакансии.

        Returns:
            Доменная сущность VacancyResponse с status='failed' или None, если не найдено.
        """
