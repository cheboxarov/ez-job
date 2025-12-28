"""Use case для отправки Telegram уведомления."""

from __future__ import annotations

from loguru import logger

from domain.entities.agent_action import AgentAction
from domain.entities.vacancy_response import VacancyResponse
from domain.interfaces.telegram_bot_port import TelegramBotPort
from domain.interfaces.telegram_notification_settings_repository_port import (
    TelegramNotificationSettingsRepositoryPort,
)


class SendTelegramNotificationUseCase:
    """Use case для отправки уведомления в Telegram."""

    def __init__(
        self,
        settings_repository: TelegramNotificationSettingsRepositoryPort,
        telegram_bot: TelegramBotPort,
        formatter,
    ) -> None:
        """Инициализация use case.

        Args:
            settings_repository: Репозиторий настроек Telegram уведомлений.
            telegram_bot: Telegram бот для отправки сообщений.
            formatter: Форматтер для форматирования уведомлений.
        """
        self._settings_repository = settings_repository
        self._telegram_bot = telegram_bot
        self._formatter = formatter

    async def execute_for_agent_action(self, action: AgentAction) -> bool:
        """Отправить уведомление о действии агента.

        Args:
            action: Действие агента.

        Returns:
            True если уведомление отправлено, False в противном случае.
        """
        try:
            settings = await self._settings_repository.get_by_user_id(action.user_id)

            if not settings or not settings.is_enabled or not settings.telegram_chat_id:
                return False

            should_notify = False
            if action.type == "send_message" and settings.notify_message_suggestion:
                should_notify = True
            elif action.type == "create_event":
                event_type = action.data.get("event_type")
                if event_type == "call_request" and settings.notify_call_request:
                    should_notify = True
                elif event_type == "external_action_request" and settings.notify_external_action:
                    should_notify = True
                elif event_type == "question_answered" and settings.notify_question_answered:
                    should_notify = True

            if not should_notify:
                return False

            text, keyboard = self._formatter.format_agent_action(action)

            success = await self._telegram_bot.send_message(
                chat_id=settings.telegram_chat_id,
                text=text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )

            if success:
                logger.info(
                    f"Telegram уведомление отправлено для action {action.id}, "
                    f"user_id={action.user_id}, chat_id={settings.telegram_chat_id}"
                )

            return success
        except Exception as exc:
            logger.error(
                f"Ошибка при отправке Telegram уведомления для action {action.id}: {exc}",
                exc_info=True,
            )
            return False

    async def execute_for_vacancy_response(self, response: VacancyResponse) -> bool:
        """Отправить уведомление об отклике на вакансию.

        Args:
            response: Отклик на вакансию.

        Returns:
            True если уведомление отправлено, False в противном случае.
        """
        try:
            settings = await self._settings_repository.get_by_user_id(response.user_id)

            if (
                not settings
                or not settings.is_enabled
                or not settings.telegram_chat_id
                or not settings.notify_vacancy_response
            ):
                return False

            text, keyboard = self._formatter.format_vacancy_response(response)

            success = await self._telegram_bot.send_message(
                chat_id=settings.telegram_chat_id,
                text=text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )

            if success:
                logger.info(
                    f"Telegram уведомление отправлено для response {response.id}, "
                    f"user_id={response.user_id}, chat_id={settings.telegram_chat_id}"
                )

            return success
        except Exception as exc:
            logger.error(
                f"Ошибка при отправке Telegram уведомления для response {response.id}: {exc}",
                exc_info=True,
            )
            return False
