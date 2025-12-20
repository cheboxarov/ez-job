"""Use case для обновления cookies пользователя после запросов к HH API."""

from __future__ import annotations

from typing import Dict
from uuid import UUID

from loguru import logger

from domain.entities.user_hh_auth_data import UserHhAuthData
from domain.interfaces.user_hh_auth_data_repository_port import (
    UserHhAuthDataRepositoryPort,
)


class UpdateUserHhAuthCookiesUseCase:
    """Use case для обновления HH auth cookies пользователя.

    Объединяет новые cookies с существующими (новые перезаписывают старые)
    и сохраняет обновленные данные в БД.
    """

    def __init__(self, repository: UserHhAuthDataRepositoryPort) -> None:
        """Инициализация use case.

        Args:
            repository: Репозиторий для работы с HH auth данными пользователя.
        """
        self._repository = repository

    async def execute(
        self,
        user_id: UUID,
        updated_cookies: Dict[str, str],
        headers: Dict[str, str] | None = None,
    ) -> UserHhAuthData:
        """Обновить cookies пользователя после запроса к HH API.

        Args:
            user_id: UUID пользователя.
            updated_cookies: Словарь обновленных cookies из ответа HH API.
            headers: Опциональные обновленные headers. Если не переданы,
                используются существующие headers.

        Returns:
            Обновленная доменная сущность UserHhAuthData.

        Raises:
            ValueError: Если auth данные для пользователя не найдены.
        """
        # Получить текущие auth данные
        current_auth = await self._repository.get_by_user_id(user_id)
        if current_auth is None:
            raise ValueError(
                f"HH auth data not found for user_id={user_id}. "
                "Please set auth data first."
            )

        # Объединить cookies (новые перезаписывают старые)
        # Важно: сохраняем все существующие cookies, обновляем только те, что пришли в ответе
        merged_cookies = {**current_auth.cookies, **updated_cookies}

        # Обновить headers если переданы, иначе использовать существующие
        final_headers = headers if headers is not None else current_auth.headers

        # Сохранить через upsert
        updated_auth = await self._repository.upsert(
            user_id=user_id,
            headers=final_headers,
            cookies=merged_cookies,
        )

        logger.debug(
            f"Updated HH auth cookies for user_id={user_id}. "
            f"Cookies updated: {len(updated_cookies)} keys"
        )

        return updated_auth
