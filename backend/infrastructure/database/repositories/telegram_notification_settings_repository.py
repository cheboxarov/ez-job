"""Реализация репозитория настроек Telegram уведомлений."""

from __future__ import annotations

from typing import Union
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from domain.entities.telegram_notification_settings import TelegramNotificationSettings
from domain.interfaces.telegram_notification_settings_repository_port import (
    TelegramNotificationSettingsRepositoryPort,
)
from infrastructure.database.models.telegram_notification_settings_model import (
    TelegramNotificationSettingsModel,
)
from infrastructure.database.repositories.base_repository import BaseRepository


class TelegramNotificationSettingsRepository(BaseRepository, TelegramNotificationSettingsRepositoryPort):
    """Реализация репозитория настроек Telegram уведомлений для SQLAlchemy."""

    def __init__(
        self, 
        session_or_factory: Union[AsyncSession, async_sessionmaker[AsyncSession]]
    ) -> None:
        """Инициализация репозитория.

        Args:
            session_or_factory: Либо AsyncSession (для транзакционного режима),
                               либо async_sessionmaker (для standalone режима).
        """
        super().__init__(session_or_factory)

    async def get_by_user_id(self, user_id: UUID) -> TelegramNotificationSettings | None:
        """Получить настройки по ID пользователя.

        Args:
            user_id: UUID пользователя.

        Returns:
            Доменная сущность TelegramNotificationSettings или None, если не найдено.
        """
        async with self._get_session() as session:
            stmt = select(TelegramNotificationSettingsModel).where(
                TelegramNotificationSettingsModel.user_id == user_id
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._to_domain(model)

    async def get_by_telegram_chat_id(self, chat_id: int) -> TelegramNotificationSettings | None:
        """Получить настройки по ID чата в Telegram.

        Args:
            chat_id: ID чата в Telegram.

        Returns:
            Доменная сущность TelegramNotificationSettings или None, если не найдено.
        """
        async with self._get_session() as session:
            stmt = select(TelegramNotificationSettingsModel).where(
                TelegramNotificationSettingsModel.telegram_chat_id == chat_id
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._to_domain(model)

    async def create(self, settings: TelegramNotificationSettings) -> TelegramNotificationSettings:
        """Создать настройки.

        Args:
            settings: Доменная сущность TelegramNotificationSettings для создания.

        Returns:
            Созданная доменная сущность TelegramNotificationSettings с заполненными id, created_at и updated_at.
        """
        async with self._get_session() as session:
            settings_id = settings.id if settings.id else uuid4()
            now = datetime.now(timezone.utc)

            model = TelegramNotificationSettingsModel(
                id=settings_id,
                user_id=settings.user_id,
                telegram_chat_id=settings.telegram_chat_id,
                telegram_username=settings.telegram_username,
                is_enabled=settings.is_enabled,
                notify_call_request=settings.notify_call_request,
                notify_external_action=settings.notify_external_action,
                notify_question_answered=settings.notify_question_answered,
                notify_message_suggestion=settings.notify_message_suggestion,
                notify_vacancy_response=settings.notify_vacancy_response,
                linked_at=settings.linked_at,
                created_at=settings.created_at if settings.created_at else now,
                updated_at=settings.updated_at if settings.updated_at else now,
            )
            session.add(model)
            await session.flush()
            await session.refresh(model)
            return self._to_domain(model)

    async def update(self, settings: TelegramNotificationSettings) -> TelegramNotificationSettings:
        """Обновить настройки.

        Args:
            settings: Доменная сущность TelegramNotificationSettings с обновленными данными.

        Returns:
            Обновленная доменная сущность TelegramNotificationSettings.

        Raises:
            ValueError: Если настройки с таким ID не найдены.
        """
        async with self._get_session() as session:
            stmt = select(TelegramNotificationSettingsModel).where(
                TelegramNotificationSettingsModel.id == settings.id
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                raise ValueError(f"Настройки с ID {settings.id} не найдены")

            model.user_id = settings.user_id
            model.telegram_chat_id = settings.telegram_chat_id
            model.telegram_username = settings.telegram_username
            model.is_enabled = settings.is_enabled
            model.notify_call_request = settings.notify_call_request
            model.notify_external_action = settings.notify_external_action
            model.notify_question_answered = settings.notify_question_answered
            model.notify_message_suggestion = settings.notify_message_suggestion
            model.notify_vacancy_response = settings.notify_vacancy_response
            model.linked_at = settings.linked_at
            model.updated_at = datetime.now(timezone.utc)

            await session.flush()
            await session.refresh(model)

            return self._to_domain(model)

    async def delete(self, user_id: UUID) -> None:
        """Удалить настройки по ID пользователя.

        Args:
            user_id: UUID пользователя.

        Raises:
            ValueError: Если настройки не найдены.
        """
        async with self._get_session() as session:
            stmt = select(TelegramNotificationSettingsModel).where(
                TelegramNotificationSettingsModel.user_id == user_id
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                raise ValueError(f"Настройки для пользователя {user_id} не найдены")

            await session.delete(model)
            await session.flush()

    def _to_domain(self, model: TelegramNotificationSettingsModel) -> TelegramNotificationSettings:
        """Преобразовать SQLAlchemy модель в доменную сущность.

        Args:
            model: SQLAlchemy модель TelegramNotificationSettingsModel.

        Returns:
            Доменная сущность TelegramNotificationSettings.
        """
        return TelegramNotificationSettings(
            id=model.id,
            user_id=model.user_id,
            telegram_chat_id=model.telegram_chat_id,
            telegram_username=model.telegram_username,
            is_enabled=model.is_enabled,
            notify_call_request=model.notify_call_request,
            notify_external_action=model.notify_external_action,
            notify_question_answered=model.notify_question_answered,
            notify_message_suggestion=model.notify_message_suggestion,
            notify_vacancy_response=model.notify_vacancy_response,
            linked_at=model.linked_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
