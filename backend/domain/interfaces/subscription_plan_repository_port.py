"""Интерфейс репозитория планов подписки."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from domain.entities.subscription_plan import SubscriptionPlan


class SubscriptionPlanRepositoryPort(ABC):
    """Порт репозитория планов подписки.

    Инфраструктура должна реализовать этот интерфейс.
    """

    @abstractmethod
    async def get_by_id(self, plan_id: UUID) -> SubscriptionPlan | None:
        """Получить план подписки по ID.

        Args:
            plan_id: UUID плана подписки.

        Returns:
            Доменная сущность SubscriptionPlan или None, если не найдено.
        """

    @abstractmethod
    async def get_by_name(self, name: str) -> SubscriptionPlan | None:
        """Получить план подписки по названию.

        Args:
            name: Название плана (FREE, PLAN_1, PLAN_2, PLAN_3).

        Returns:
            Доменная сущность SubscriptionPlan или None, если не найдено.
        """

    @abstractmethod
    async def get_all(self) -> List[SubscriptionPlan]:
        """Получить все активные планы подписки.

        Returns:
            Список доменных сущностей SubscriptionPlan.
        """
