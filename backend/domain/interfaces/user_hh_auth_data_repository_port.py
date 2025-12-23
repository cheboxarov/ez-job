"""Интерфейс репозитория для HH auth data пользователя."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.user_hh_auth_data import UserHhAuthData


class UserHhAuthDataRepositoryPort(ABC):
    """Порт репозитория для работы с HH auth data пользователя."""

    @abstractmethod
    async def get_by_user_id(
        self, user_id: UUID, *, with_for_update: bool = False
    ) -> UserHhAuthData | None:
        """Получить HH auth data по user_id.

        Args:
            user_id: UUID пользователя.
            with_for_update: Использовать SELECT ... FOR UPDATE (блокировка строки).

        Returns:
            Доменная сущность UserHhAuthData или None, если не найдено.
        """

    @abstractmethod
    async def upsert(
        self,
        user_id: UUID,
        headers: dict[str, str],
        cookies: dict[str, str],
    ) -> UserHhAuthData:
        """Создать или обновить HH auth data для пользователя.

        Args:
            user_id: UUID пользователя.
            headers: Словарь headers для HH API.
            cookies: Словарь cookies для HH API.

        Returns:
            Сохраненная доменная сущность UserHhAuthData.
        """

    @abstractmethod
    async def delete(self, user_id: UUID) -> None:
        """Удалить HH auth data для пользователя.

        Args:
            user_id: UUID пользователя.
        """
