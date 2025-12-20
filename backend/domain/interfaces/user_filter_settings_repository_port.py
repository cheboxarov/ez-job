"""Интерфейс репозитория настроек фильтров пользователя."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.user_filter_settings import UserFilterSettings


class UserFilterSettingsRepositoryPort(ABC):
    """Порт репозитория настроек фильтров пользователя."""

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> UserFilterSettings | None:
        """Получить настройки фильтров по ID пользователя."""

    @abstractmethod
    async def upsert_for_user(
        self,
        user_id: UUID,
        settings: UserFilterSettings,
    ) -> UserFilterSettings:
        """Создать или обновить настройки фильтров для пользователя."""


