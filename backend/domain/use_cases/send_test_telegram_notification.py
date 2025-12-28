"""Use case для отправки тестового Telegram уведомления."""

from __future__ import annotations

from uuid import UUID

from loguru import logger

from domain.interfaces.telegram_bot_port import TelegramBotPort
from domain.interfaces.telegram_notification_settings_repository_port import (
    TelegramNotificationSettingsRepositoryPort,
)


class SendTestTelegramNotificationUseCase:
    """Use case для отправки тестового уведомления в Telegram."""

    def __init__(
        self,
        settings_repository: TelegramNotificationSettingsRepositoryPort,
        telegram_bot: TelegramBotPort,
    ) -> None:
        """Инициализация use case.

        Args:
            settings_repository: Репозиторий настроек Telegram уведомлений.
            telegram_bot: Telegram бот для отправки сообщений.
        """
        self._settings_repository = settings_repository
        self._telegram_bot = telegram_bot

    async def execute(self, user_id: UUID) -> bool:
        """Отправить тестовое уведомление.

        Args:
            user_id: UUID пользователя.

        Returns:
            True если уведомление отправлено, False в противном случае.

        Raises:
            ValueError: Если Telegram не привязан.
        """
        try:
            settings = await self._settings_repository.get_by_user_id(user_id)

            if not settings or not settings.telegram_chat_id:
                raise ValueError("Telegram аккаунт не привязан")

            text = (
                "🔔 <b>Тестовое уведомление</b>\n\n"
                "Если вы видите это сообщение — уведомления работают!"
            )

            success = await self._telegram_bot.send_message(
                chat_id=settings.telegram_chat_id,
                text=text,
                parse_mode="HTML",
                reply_markup=None,
            )

            if success:
                logger.info(
                    f"Тестовое Telegram уведомление отправлено для user_id={user_id}, "
                    f"chat_id={settings.telegram_chat_id}"
                )

            return success
        except ValueError:
            raise
        except Exception as exc:
            logger.error(
                f"Ошибка при отправке тестового Telegram уведомления для user_id={user_id}: {exc}",
                exc_info=True,
            )
            return False
