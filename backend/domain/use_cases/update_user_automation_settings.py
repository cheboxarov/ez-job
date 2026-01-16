"""Use case для обновления настроек автоматизации пользователя."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from loguru import logger

from domain.entities.user_automation_settings import UserAutomationSettings
from domain.interfaces.user_automation_settings_repository_port import (
    UserAutomationSettingsRepositoryPort,
)


class UpdateUserAutomationSettingsUseCase:
    """Use case для обновления настроек автоматизации пользователя."""

    def __init__(self, settings_repository: UserAutomationSettingsRepositoryPort) -> None:
        """Инициализация use case.

        Args:
            settings_repository: Репозиторий настроек автоматизации пользователя.
        """
        self._settings_repository = settings_repository

    async def execute(
        self,
        user_id: UUID,
        *,
        auto_reply_to_questions_in_chats: bool | None = None,
        auto_watch_chats: bool | None = None,
    ) -> UserAutomationSettings:
        """Обновить настройки автоматизации пользователя.

        Args:
            user_id: UUID пользователя.
            auto_reply_to_questions_in_chats: Автоматически отвечать на вопросы в чатах.

        Returns:
            Обновленная доменная сущность UserAutomationSettings.

        Raises:
            ValueError: Если настройки не найдены.
            Exception: При ошибках работы с БД.
        """
        try:
            settings = await self._settings_repository.get_by_user_id(user_id)

            if settings is None:
                raise ValueError(f"Настройки автоматизации для пользователя {user_id} не найдены")

            if auto_reply_to_questions_in_chats is not None:
                settings.auto_reply_to_questions_in_chats = auto_reply_to_questions_in_chats
            
            if auto_watch_chats is not None:
                settings.auto_watch_chats = auto_watch_chats

            settings.updated_at = datetime.now(timezone.utc)

            updated_settings = await self._settings_repository.update(settings)

            logger.info(f"Настройки автоматизации обновлены для пользователя {user_id}")

            return updated_settings
        except ValueError:
            raise
        except Exception as exc:
            logger.error(
                f"Ошибка при обновлении настроек автоматизации для пользователя {user_id}: {exc}",
                exc_info=True,
            )
            raise
