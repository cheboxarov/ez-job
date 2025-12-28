"""Use case для обновления настроек Telegram уведомлений."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from loguru import logger

from domain.entities.telegram_notification_settings import TelegramNotificationSettings
from domain.interfaces.telegram_notification_settings_repository_port import (
    TelegramNotificationSettingsRepositoryPort,
)


class UpdateTelegramNotificationSettingsUseCase:
    """Use case для обновления настроек Telegram уведомлений."""

    def __init__(self, settings_repository: TelegramNotificationSettingsRepositoryPort) -> None:
        """Инициализация use case.

        Args:
            settings_repository: Репозиторий настроек Telegram уведомлений.
        """
        self._settings_repository = settings_repository

    async def execute(
        self,
        user_id: UUID,
        *,
        is_enabled: bool | None = None,
        notify_call_request: bool | None = None,
        notify_external_action: bool | None = None,
        notify_question_answered: bool | None = None,
        notify_message_suggestion: bool | None = None,
        notify_vacancy_response: bool | None = None,
    ) -> TelegramNotificationSettings:
        """Обновить настройки Telegram уведомлений.

        Если Telegram не привязан, нельзя включить is_enabled.

        Args:
            user_id: UUID пользователя.
            is_enabled: Глобальный переключатель уведомлений.
            notify_call_request: Уведомлять о собеседованиях.
            notify_external_action: Уведомлять о требуемых действиях.
            notify_question_answered: Уведомлять об ответах на вопросы.
            notify_message_suggestion: Уведомлять о предложенных сообщениях.
            notify_vacancy_response: Уведомлять об отправленных откликах.

        Raises:
            ValueError: Если пытаются включить уведомления без привязки Telegram.
            Exception: При ошибках работы с БД.
        """
        try:
            settings = await self._settings_repository.get_by_user_id(user_id)

            if settings is None:
                raise ValueError(f"Настройки Telegram для пользователя {user_id} не найдены")

            if is_enabled is not None:
                if is_enabled and settings.telegram_chat_id is None:
                    raise ValueError("Нельзя включить уведомления без привязки Telegram")
                settings.is_enabled = is_enabled

            if notify_call_request is not None:
                settings.notify_call_request = notify_call_request
            if notify_external_action is not None:
                settings.notify_external_action = notify_external_action
            if notify_question_answered is not None:
                settings.notify_question_answered = notify_question_answered
            if notify_message_suggestion is not None:
                settings.notify_message_suggestion = notify_message_suggestion
            if notify_vacancy_response is not None:
                settings.notify_vacancy_response = notify_vacancy_response

            settings.updated_at = datetime.now(timezone.utc)

            updated_settings = await self._settings_repository.update(settings)

            logger.info(f"Настройки Telegram уведомлений обновлены для пользователя {user_id}")
            
            return updated_settings
        except ValueError:
            raise
        except Exception as exc:
            logger.error(
                f"Ошибка при обновлении настроек Telegram для пользователя {user_id}: {exc}",
                exc_info=True,
            )
            raise
