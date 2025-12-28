"""Use case для отвязки Telegram аккаунта."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from loguru import logger

from domain.interfaces.telegram_notification_settings_repository_port import (
    TelegramNotificationSettingsRepositoryPort,
)


class UnlinkTelegramAccountUseCase:
    """Use case для отвязки Telegram аккаунта."""

    def __init__(self, settings_repository: TelegramNotificationSettingsRepositoryPort) -> None:
        """Инициализация use case.

        Args:
            settings_repository: Репозиторий настроек Telegram уведомлений.
        """
        self._settings_repository = settings_repository

    async def execute(self, user_id: UUID) -> None:
        """Отвязать Telegram аккаунт.

        Обнуляет telegram_chat_id и отключает уведомления.

        Args:
            user_id: UUID пользователя.

        Raises:
            ValueError: Если настройки не найдены.
            Exception: При ошибках работы с БД.
        """
        try:
            settings = await self._settings_repository.get_by_user_id(user_id)

            if settings is None:
                raise ValueError(f"Настройки Telegram для пользователя {user_id} не найдены")

            settings.telegram_chat_id = None
            settings.telegram_username = None
            settings.is_enabled = False
            settings.linked_at = None
            settings.updated_at = datetime.now(timezone.utc)

            await self._settings_repository.update(settings)

            logger.info(f"Telegram аккаунт отвязан для пользователя {user_id}")
        except ValueError:
            raise
        except Exception as exc:
            logger.error(
                f"Ошибка при отвязке Telegram аккаунта для пользователя {user_id}: {exc}",
                exc_info=True,
            )
            raise
