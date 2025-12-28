"""Интерфейс репозитория токенов привязки Telegram."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.telegram_link_token import TelegramLinkToken


class TelegramLinkTokenRepositoryPort(ABC):
    """Порт репозитория токенов привязки Telegram.

    Инфраструктура должна реализовать этот интерфейс.
    """

    @abstractmethod
    async def create(self, token: TelegramLinkToken) -> TelegramLinkToken:
        """Создать токен.

        Args:
            token: Доменная сущность TelegramLinkToken для создания.

        Returns:
            Созданная доменная сущность TelegramLinkToken с заполненными id и created_at.
        """

    @abstractmethod
    async def get_by_token(self, token_str: str) -> TelegramLinkToken | None:
        """Получить токен по строке токена.

        Args:
            token_str: Строка токена.

        Returns:
            Доменная сущность TelegramLinkToken или None, если не найдено.
        """

    @abstractmethod
    async def delete_by_user_id(self, user_id: UUID) -> None:
        """Удалить все токены пользователя.

        Args:
            user_id: UUID пользователя.
        """

    @abstractmethod
    async def delete_expired(self) -> None:
        """Удалить все истёкшие токены."""