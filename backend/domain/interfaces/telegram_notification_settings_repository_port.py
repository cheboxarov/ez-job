"""Интерфейс репозитория настроек Telegram уведомлений."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.telegram_notification_settings import TelegramNotificationSettings


class TelegramNotificationSettingsRepositoryPort(ABC):
    """Порт репозитория настроек Telegram уведомлений.

    Инфраструктура должна реализовать этот интерфейс.
    """

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> TelegramNotificationSettings | None:
        """Получить настройки по ID пользователя.

        Args:
            user_id: UUID пользователя.

        Returns:
            Доменная сущность TelegramNotificationSettings или None, если не найдено.
        """

    @abstractmethod
    async def get_by_telegram_chat_id(self, chat_id: int) -> TelegramNotificationSettings | None:
        """Получить настройки по ID чата в Telegram.

        Args:
            chat_id: ID чата в Telegram.

        Returns:
            Доменная сущность TelegramNotificationSettings или None, если не найдено.
        """

    @abstractmethod
    async def create(self, settings: TelegramNotificationSettings) -> TelegramNotificationSettings:
        """Создать настройки.

        Args:
            settings: Доменная сущность TelegramNotificationSettings для создания.

        Returns:
            Созданная доменная сущность TelegramNotificationSettings с заполненными id, created_at и updated_at.
        """

    @abstractmethod
    async def update(self, settings: TelegramNotificationSettings) -> TelegramNotificationSettings:
        """Обновить настройки.

        Args:
            settings: Доменная сущность TelegramNotificationSettings с обновленными данными.

        Returns:
            Обновленная доменная сущность TelegramNotificationSettings.

        Raises:
            ValueError: Если настройки с таким ID не найдены.
        """

    @abstractmethod
    async def delete(self, user_id: UUID) -> None:
        """Удалить настройки по ID пользователя.

        Args:
            user_id: UUID пользователя.

        Raises:
            ValueError: Если настройки не найдены.
        """
