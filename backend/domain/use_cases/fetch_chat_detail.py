"""Use case для получения детальной информации об одном чате."""

from __future__ import annotations

from typing import Dict, Optional
from uuid import UUID

from domain.entities.hh_chat_detailed import HHChatDetailed
from domain.interfaces.hh_client_port import HHClientPort
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase
from infrastructure.clients.hh_client_with_cookie_update import HHHttpClientWithCookieUpdate


class FetchChatDetailUseCase:
    """Use case получения детальной информации об одном чате с сообщениями."""

    def __init__(self, hh_client: HHClientPort) -> None:
        """Инициализация use case.

        Args:
            hh_client: HH клиент для выполнения запросов.
        """
        self._hh_client = hh_client

    async def execute(
        self,
        chat_id: int,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        user_id: Optional[UUID] = None,
        update_cookies_uc: Optional[UpdateUserHhAuthCookiesUseCase] = None,
    ) -> Optional[HHChatDetailed]:
        """Получить детальную информацию об одном чате с сообщениями.

        Args:
            chat_id: ID чата для получения детальной информации.
            headers: HTTP заголовки для запросов к HH API.
            cookies: HTTP cookies для запросов к HH API.
            user_id: UUID пользователя для обновления cookies (опционально).
            update_cookies_uc: Use case для обновления cookies (опционально).

        Returns:
            Детальная информация о чате или None, если чат не найден.
        """
        # Если передан user_id и update_cookies_uc, используем обертку для автоматического сохранения cookies
        if user_id and update_cookies_uc:
            client = HHHttpClientWithCookieUpdate(self._hh_client, user_id, update_cookies_uc)
        else:
            client = self._hh_client

        return await client.fetch_chat_detail(
            chat_id=chat_id,
            headers=headers,
            cookies=cookies,
        )

