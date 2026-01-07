"""Интерфейс репозитория настроек автоматизации пользователя."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.user_automation_settings import UserAutomationSettings


class UserAutomationSettingsRepositoryPort(ABC):
    """Порт репозитория настроек автоматизации пользователя.

    Инфраструктура должна реализовать этот интерфейс.
    """

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> UserAutomationSettings | None:
        """Получить настройки по ID пользователя.

        Args:
            user_id: UUID пользователя.

        Returns:
            Доменная сущность UserAutomationSettings или None, если не найдено.
        """

    @abstractmethod
    async def create(self, settings: UserAutomationSettings) -> UserAutomationSettings:
        """Создать настройки.

        Args:
            settings: Доменная сущность UserAutomationSettings для создания.

        Returns:
            Созданная доменная сущность UserAutomationSettings с заполненными id, created_at и updated_at.
        """

    @abstractmethod
    async def update(self, settings: UserAutomationSettings) -> UserAutomationSettings:
        """Обновить настройки.

        Args:
            settings: Доменная сущность UserAutomationSettings с обновленными данными.

        Returns:
            Обновленная доменная сущность UserAutomationSettings.

        Raises:
            ValueError: Если настройки с таким ID не найдены.
        """
