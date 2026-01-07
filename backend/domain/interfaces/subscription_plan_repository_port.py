"""Интерфейс репозитория планов подписки."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Tuple
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

    @abstractmethod
    async def list_for_admin(
        self,
        page: int,
        page_size: int,
    ) -> Tuple[List[SubscriptionPlan], int]:
        """Получить планы подписки для админки с пагинацией.

        Args:
            page: Номер страницы (начиная с 1).
            page_size: Размер страницы.

        Returns:
            Кортеж (список планов, общее количество планов).
        """

    @abstractmethod
    async def create(self, plan: SubscriptionPlan) -> SubscriptionPlan:
        """Создать новый план подписки."""

    @abstractmethod
    async def update(self, plan: SubscriptionPlan) -> SubscriptionPlan:
        """Обновить существующий план подписки."""

    @abstractmethod
    async def delete(self, plan_id: UUID) -> None:
        """Удалить план подписки по ID."""
