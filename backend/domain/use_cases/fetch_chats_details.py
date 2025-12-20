from __future__ import annotations

import asyncio
from typing import Dict, List, Optional
from uuid import UUID

from domain.entities.hh_chat_detailed import HHChatDetailed
from domain.interfaces.hh_client_port import HHClientPort
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase
from infrastructure.clients.hh_client_with_cookie_update import HHHttpClientWithCookieUpdate


class FetchChatsDetailsUseCase:
    """Use case получения детальной информации о чатах с сообщениями."""

    def __init__(self, hh_client: HHClientPort) -> None:
        self._hh_client = hh_client

    async def execute(
        self,
        chat_ids: List[int],
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        user_id: Optional[UUID] = None,
        update_cookies_uc: Optional[UpdateUserHhAuthCookiesUseCase] = None,
    ) -> List[HHChatDetailed]:
        """Получить детальную информацию о чатах с сообщениями.

        Args:
            chat_ids: Список ID чатов для получения детальной информации.
            headers: HTTP заголовки для запросов к HH API.
            cookies: HTTP cookies для запросов к HH API.
            user_id: UUID пользователя для обновления cookies (опционально).
            update_cookies_uc: Use case для обновления cookies (опционально).

        Returns:
            Список детальной информации о чатах (только успешно полученные).
        """
        # Если передан user_id и update_cookies_uc, используем обертку для автоматического сохранения cookies
        if user_id and update_cookies_uc:
            client = HHHttpClientWithCookieUpdate(self._hh_client, user_id, update_cookies_uc)
        else:
            client = self._hh_client
        # Параллельно получаем детальную информацию о каждом чате
        tasks = [
            client.fetch_chat_detail(chat_id, headers, cookies)
            for chat_id in chat_ids
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Фильтруем только успешно полученные чаты
        chats: List[HHChatDetailed] = []
        for result in results:
            if isinstance(result, HHChatDetailed):
                chats.append(result)
            elif isinstance(result, Exception):
                print(f"[fetch_chats_details] Ошибка получения чата: {result}", flush=True)

        return chats

