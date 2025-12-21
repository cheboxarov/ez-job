from __future__ import annotations

from typing import Dict, Optional
from uuid import UUID

from domain.entities.hh_list_chat import HHListChat
from domain.interfaces.hh_client_port import HHClientPort
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase
from infrastructure.clients.hh_client_with_cookie_update import HHHttpClientWithCookieUpdate


class FetchUserChatsUseCase:
    """Use case получения списка чатов пользователя."""

    def __init__(self, hh_client: HHClientPort) -> None:
        self._hh_client = hh_client

    async def execute(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        user_id: Optional[UUID] = None,
        update_cookies_uc: Optional[UpdateUserHhAuthCookiesUseCase] = None,
    ) -> HHListChat:
        """Получить список всех чатов пользователя.

        Args:
            headers: HTTP заголовки для запросов к HH API.
            cookies: HTTP cookies для запросов к HH API.
            user_id: UUID пользователя для обновления cookies (опционально).
            update_cookies_uc: Use case для обновления cookies (опционально).

        Returns:
            Список чатов пользователя.
        """
        # Если передан user_id и update_cookies_uc, используем обертку для автоматического сохранения cookies
        if user_id and update_cookies_uc:
            client = HHHttpClientWithCookieUpdate(self._hh_client, user_id, update_cookies_uc)
        else:
            client = self._hh_client
        # Вызываем fetch_chat_list с пустым списком ID для получения всех чатов
        return await client.fetch_chat_list(
            chat_ids=[],
            headers=headers,
            cookies=cookies,
            filter_unread=True,
        )

