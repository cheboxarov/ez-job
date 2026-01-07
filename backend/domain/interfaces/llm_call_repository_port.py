"""Интерфейс репозитория для логирования вызовов LLM."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from domain.entities.llm_call import LlmCall


class LlmCallRepositoryPort(ABC):
    """Порт репозитория для логирования вызовов LLM.

    Инфраструктура должна реализовать этот интерфейс.
    """

    @abstractmethod
    async def create(self, llm_call: LlmCall) -> LlmCall:
        """Создать запись о вызове LLM.

        Args:
            llm_call: Доменная сущность LlmCall для создания.
                     Поле id может быть не заполнено (будет сгенерировано).

        Returns:
            Созданная доменная сущность LlmCall с заполненными id и created_at.
        """

    @abstractmethod
    async def get_by_id(self, call_id: UUID) -> LlmCall | None:
        """Получить запись о вызове LLM по ID.

        Args:
            call_id: UUID записи.

        Returns:
            Доменная сущность LlmCall или None, если не найдено.
        """

    @abstractmethod
    async def list_for_admin(
        self,
        *,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        user_id: UUID | None = None,
        agent_name: str | None = None,
        status: str | None = None,
        page: int,
        page_size: int,
    ) -> tuple[list[LlmCall], int]:
        """Получить список вызовов LLM для админки с фильтрами и пагинацией.

        Args:
            start_date: Начальная дата фильтра (включительно).
            end_date: Конечная дата фильтра (включительно).
            user_id: Фильтр по ID пользователя.
            agent_name: Фильтр по имени агента.
            status: Фильтр по статусу ('success' или 'error').
            page: Номер страницы (начиная с 1).
            page_size: Размер страницы.

        Returns:
            Кортеж из списка LlmCall и общего количества записей.
        """

    @abstractmethod
    async def get_metrics_by_period(
        self,
        *,
        start_date: datetime,
        end_date: datetime,
        plan_id: UUID | None = None,
        time_step: str = "day",
    ) -> list[tuple[datetime, int, int, int]]:
        """Получить метрики LLM по периоду с группировкой по времени.

        Args:
            start_date: Начальная дата (включительно).
            end_date: Конечная дата (включительно).
            plan_id: Фильтр по ID плана подписки (опционально).
            time_step: Шаг группировки ('day', 'week', 'month').

        Returns:
            Список кортежей (дата/время начала периода, количество вызовов,
            суммарные токены, количество уникальных пользователей).
        """

    @abstractmethod
    async def get_total_metrics(
        self,
        *,
        start_date: datetime,
        end_date: datetime,
        plan_id: UUID | None = None,
    ) -> tuple[int, int, int, float]:
        """Получить суммарные метрики LLM за период.

        Args:
            start_date: Начальная дата (включительно).
            end_date: Конечная дата (включительно).
            plan_id: Фильтр по ID плана подписки (опционально).

        Returns:
            Кортеж (общее количество вызовов, суммарные токены,
            количество уникальных пользователей, средние токены на пользователя).
        """
