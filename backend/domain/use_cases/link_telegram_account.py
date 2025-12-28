"""Use case для привязки Telegram аккаунта."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from loguru import logger

from domain.entities.telegram_notification_settings import TelegramNotificationSettings
from domain.interfaces.telegram_link_token_repository_port import TelegramLinkTokenRepositoryPort
from domain.interfaces.telegram_notification_settings_repository_port import (
    TelegramNotificationSettingsRepositoryPort,
)


class LinkTelegramAccountUseCase:
    """Use case для привязки Telegram аккаунта по токену."""

    def __init__(
        self,
        token_repository: TelegramLinkTokenRepositoryPort,
        settings_repository: TelegramNotificationSettingsRepositoryPort,
    ) -> None:
        """Инициализация use case.

        Args:
            token_repository: Репозиторий токенов привязки.
            settings_repository: Репозиторий настроек Telegram уведомлений.
        """
        self._token_repository = token_repository
        self._settings_repository = settings_repository

    async def execute(
        self,
        telegram_chat_id: int,
        telegram_username: str | None,
        token: str,
    ) -> TelegramNotificationSettings:
        """Привязать Telegram аккаунт по токену.

        Args:
            telegram_chat_id: ID чата в Telegram.
            telegram_username: Username пользователя в Telegram (опционально).
            token: Токен привязки.

        Returns:
            Обновленная доменная сущность TelegramNotificationSettings.

        Raises:
            ValueError: Если токен недействителен или истёк.
            Exception: При ошибках работы с БД.
        """
        try:
            link_token = await self._token_repository.get_by_token(token)

            if link_token is None:
                raise ValueError("Токен привязки не найден")

            if datetime.now(timezone.utc) > link_token.expires_at:
                await self._token_repository.delete_by_user_id(link_token.user_id)
                raise ValueError("Токен привязки истёк")

            user_id = link_token.user_id

            existing_settings = await self._settings_repository.get_by_user_id(user_id)

            now = datetime.now(timezone.utc)

            if existing_settings is None:
                settings = TelegramNotificationSettings(
                    id=uuid4(),
                    user_id=user_id,
                    telegram_chat_id=telegram_chat_id,
                    telegram_username=telegram_username,
                    is_enabled=False,
                    notify_call_request=True,
                    notify_external_action=True,
                    notify_question_answered=True,
                    notify_message_suggestion=True,
                    notify_vacancy_response=True,
                    linked_at=now,
                    created_at=now,
                    updated_at=now,
                )
                settings = await self._settings_repository.create(settings)
            else:
                existing_settings.telegram_chat_id = telegram_chat_id
                existing_settings.telegram_username = telegram_username
                existing_settings.linked_at = now
                existing_settings.updated_at = now
                settings = await self._settings_repository.update(existing_settings)

            await self._token_repository.delete_by_user_id(user_id)

            logger.info(
                f"Telegram аккаунт привязан: user_id={user_id}, "
                f"chat_id={telegram_chat_id}, username={telegram_username}"
            )

            return settings
        except ValueError:
            raise
        except Exception as exc:
            logger.error(
                f"Ошибка при привязке Telegram аккаунта chat_id={telegram_chat_id}, token={token}: {exc}",
                exc_info=True,
            )
            raise
