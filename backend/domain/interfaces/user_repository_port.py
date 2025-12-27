"""Интерфейс репозитория пользователя."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.user import User


class UserRepositoryPort(ABC):
    """Порт репозитория пользователя.

    Инфраструктура должна реализовать этот интерфейс.
    """

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Получить пользователя по ID.

        Args:
            user_id: UUID пользователя.

        Returns:
            Доменная сущность User или None, если пользователь не найден.
        """

    @abstractmethod
    async def get_first(self) -> User | None:
        """Получить первого пользователя из БД.

        Returns:
            Доменная сущность User или None, если пользователи не найдены.
        """

    @abstractmethod
    async def list_all(self) -> list[User]:
        """Получить всех пользователей из БД.

        Returns:
            Список доменных сущностей User.
        """

    @abstractmethod
    async def update(self, user: User) -> User:
        """Обновить пользователя.

        Args:
            user: Доменная сущность User с обновленными данными.

        Returns:
            Обновленная доменная сущность User.

        Raises:
            ValueError: Если пользователь с таким ID не найден.
        """

