"""Интерфейс репозитория подписок пользователей."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.user_subscription import UserSubscription


class UserSubscriptionRepositoryPort(ABC):
    """Порт репозитория подписок пользователей.

    Инфраструктура должна реализовать этот интерфейс.
    """

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> UserSubscription | None:
        """Получить подписку пользователя по user_id.

        Args:
            user_id: UUID пользователя.

        Returns:
            Доменная сущность UserSubscription или None, если не найдено.
        """

    @abstractmethod
    async def create(self, user_subscription: UserSubscription) -> UserSubscription:
        """Создать подписку пользователя.

        Args:
            user_subscription: Доменная сущность UserSubscription для создания.

        Returns:
            Созданная доменная сущность UserSubscription.
        """

    @abstractmethod
    async def update(self, user_subscription: UserSubscription) -> UserSubscription:
        """Обновить подписку пользователя.

        Args:
            user_subscription: Доменная сущность UserSubscription с обновленными данными.

        Returns:
            Обновленная доменная сущность UserSubscription.

        Raises:
            ValueError: Если подписка с таким user_id не найдена.
        """
