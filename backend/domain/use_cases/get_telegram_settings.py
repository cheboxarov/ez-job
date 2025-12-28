"""Use case для получения настроек Telegram уведомлений."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from loguru import logger

from domain.entities.telegram_notification_settings import TelegramNotificationSettings
from domain.interfaces.telegram_notification_settings_repository_port import (
    TelegramNotificationSettingsRepositoryPort,
)


class GetTelegramSettingsUseCase:
    """Use case для получения настроек Telegram уведомлений.

    Если настройки не существуют, создаёт их с дефолтными значениями.
    """

    def __init__(self, settings_repository: TelegramNotificationSettingsRepositoryPort) -> None:
        """Инициализация use case.

        Args:
            settings_repository: Репозиторий настроек Telegram уведомлений.
        """
        self._settings_repository = settings_repository

    async def execute(self, user_id: UUID) -> TelegramNotificationSettings:
        """Получить настройки Telegram уведомлений.

        Если настройки не существуют, создаёт их с дефолтными значениями.

        Args:
            user_id: UUID пользователя.

        Returns:
            Доменная сущность TelegramNotificationSettings.

        Raises:
            Exception: При ошибках работы с БД.
        """
        try:
            settings = await self._settings_repository.get_by_user_id(user_id)

            if settings is None:
                now = datetime.now(timezone.utc)
                settings = TelegramNotificationSettings(
                    id=uuid4(),
                    user_id=user_id,
                    telegram_chat_id=None,
                    telegram_username=None,
                    is_enabled=False,
                    notify_call_request=True,
                    notify_external_action=True,
                    notify_question_answered=True,
                    notify_message_suggestion=True,
                    notify_vacancy_response=True,
                    linked_at=None,
                    created_at=now,
                    updated_at=now,
                )
                settings = await self._settings_repository.create(settings)
                logger.info(f"Созданы дефолтные настройки Telegram для пользователя {user_id}")

            return settings
        except Exception as exc:
            logger.error(
                f"Ошибка при получении настроек Telegram для пользователя {user_id}: {exc}",
                exc_info=True,
            )
            raise
