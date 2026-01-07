"""Реализация репозитория настроек автоматизации пользователя."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.user_automation_settings import UserAutomationSettings
from domain.interfaces.user_automation_settings_repository_port import (
    UserAutomationSettingsRepositoryPort,
)
from infrastructure.database.models.user_automation_settings_model import (
    UserAutomationSettingsModel,
)


class UserAutomationSettingsRepository(UserAutomationSettingsRepositoryPort):
    """Реализация репозитория настроек автоматизации пользователя для SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория.

        Args:
            session: Async сессия SQLAlchemy.
        """
        self._session = session

    async def get_by_user_id(self, user_id: UUID) -> UserAutomationSettings | None:
        """Получить настройки по ID пользователя.

        Args:
            user_id: UUID пользователя.

        Returns:
            Доменная сущность UserAutomationSettings или None, если не найдено.
        """
        stmt = select(UserAutomationSettingsModel).where(
            UserAutomationSettingsModel.user_id == user_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def create(self, settings: UserAutomationSettings) -> UserAutomationSettings:
        """Создать настройки.

        Args:
            settings: Доменная сущность UserAutomationSettings для создания.

        Returns:
            Созданная доменная сущность UserAutomationSettings с заполненными id, created_at и updated_at.
        """
        settings_id = settings.id if settings.id else uuid4()
        now = datetime.now(timezone.utc)

        model = UserAutomationSettingsModel(
            id=settings_id,
            user_id=settings.user_id,
            auto_reply_to_questions_in_chats=settings.auto_reply_to_questions_in_chats,
            created_at=settings.created_at if settings.created_at else now,
            updated_at=settings.updated_at if settings.updated_at else now,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def update(self, settings: UserAutomationSettings) -> UserAutomationSettings:
        """Обновить настройки.

        Args:
            settings: Доменная сущность UserAutomationSettings с обновленными данными.

        Returns:
            Обновленная доменная сущность UserAutomationSettings.

        Raises:
            ValueError: Если настройки с таким ID не найдены.
        """
        stmt = select(UserAutomationSettingsModel).where(
            UserAutomationSettingsModel.id == settings.id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            raise ValueError(f"Настройки с ID {settings.id} не найдены")

        model.user_id = settings.user_id
        model.auto_reply_to_questions_in_chats = settings.auto_reply_to_questions_in_chats
        model.updated_at = datetime.now(timezone.utc)

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_domain(model)

    def _to_domain(self, model: UserAutomationSettingsModel) -> UserAutomationSettings:
        """Преобразовать SQLAlchemy модель в доменную сущность.

        Args:
            model: SQLAlchemy модель UserAutomationSettingsModel.

        Returns:
            Доменная сущность UserAutomationSettings.
        """
        return UserAutomationSettings(
            id=model.id,
            user_id=model.user_id,
            auto_reply_to_questions_in_chats=model.auto_reply_to_questions_in_chats,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
