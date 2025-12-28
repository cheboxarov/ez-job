"""Use case для генерации токена привязки Telegram."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from loguru import logger

from domain.entities.telegram_link_token import TelegramLinkToken
from domain.interfaces.telegram_link_token_repository_port import TelegramLinkTokenRepositoryPort


class GenerateTelegramLinkTokenUseCase:
    """Use case для генерации временного токена привязки Telegram."""

    def __init__(
        self,
        token_repository: TelegramLinkTokenRepositoryPort,
        token_ttl_seconds: int = 600,
    ) -> None:
        """Инициализация use case.

        Args:
            token_repository: Репозиторий токенов привязки.
            token_ttl_seconds: Время жизни токена в секундах (по умолчанию 10 минут).
        """
        self._token_repository = token_repository
        self._token_ttl_seconds = token_ttl_seconds

    async def execute(self, user_id: UUID) -> str:
        """Сгенерировать токен для привязки Telegram.

        Удаляет предыдущие токены пользователя перед созданием нового.

        Args:
            user_id: UUID пользователя.

        Returns:
            Сгенерированный токен (строка).

        Raises:
            Exception: При ошибках работы с БД.
        """
        try:
            await self._token_repository.delete_by_user_id(user_id)

            token_str = secrets.token_urlsafe(32)

            expires_at = datetime.now(timezone.utc) + timedelta(seconds=self._token_ttl_seconds)

            token = TelegramLinkToken(
                id=uuid4(),
                user_id=user_id,
                token=token_str,
                expires_at=expires_at,
                created_at=datetime.now(timezone.utc),
            )

            await self._token_repository.create(token)
            logger.info(f"Создан токен привязки Telegram для пользователя {user_id}, expires_at={expires_at}")

            return token_str
        except Exception as exc:
            logger.error(
                f"Ошибка при генерации токена привязки для пользователя {user_id}: {exc}",
                exc_info=True,
            )
            raise
