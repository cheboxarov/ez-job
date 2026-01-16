"""Use case для получения настроек автоматизации пользователя."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from loguru import logger

from domain.entities.user_automation_settings import UserAutomationSettings
from domain.interfaces.user_automation_settings_repository_port import (
    UserAutomationSettingsRepositoryPort,
)


class GetUserAutomationSettingsUseCase:
    """Use case для получения настроек автоматизации пользователя.

    Если настройки не существуют, создаёт их с дефолтными значениями.
    """

    def __init__(self, settings_repository: UserAutomationSettingsRepositoryPort) -> None:
        """Инициализация use case.

        Args:
            settings_repository: Репозиторий настроек автоматизации пользователя.
        """
        self._settings_repository = settings_repository

    async def execute(self, user_id: UUID) -> UserAutomationSettings:
        """Получить настройки автоматизации пользователя.

        Если настройки не существуют, создаёт их с дефолтными значениями.

        Args:
            user_id: UUID пользователя.

        Returns:
            Доменная сущность UserAutomationSettings.

        Raises:
            Exception: При ошибках работы с БД.
        """
        try:
            settings = await self._settings_repository.get_by_user_id(user_id)

            if settings is None:
                now = datetime.now(timezone.utc)
                settings = UserAutomationSettings(
                    id=uuid4(),
                    user_id=user_id,
                    auto_reply_to_questions_in_chats=False,
                    auto_watch_chats=True,
                    created_at=now,
                    updated_at=now,
                )
                settings = await self._settings_repository.create(settings)
                logger.info(f"Созданы дефолтные настройки автоматизации для пользователя {user_id}")

            return settings
        except Exception as exc:
            logger.error(
                f"Ошибка при получении настроек автоматизации для пользователя {user_id}: {exc}",
                exc_info=True,
            )
            raise
