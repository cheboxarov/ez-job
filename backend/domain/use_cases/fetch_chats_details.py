from __future__ import annotations

import asyncio
from typing import Dict, List

from loguru import logger

from domain.entities.hh_chat_detailed import HHChatDetailed
from domain.interfaces.hh_client_port import HHClientPort


class FetchChatsDetailsUseCase:
    """Use case получения детальной информации о чатах с сообщениями."""

    def __init__(self, hh_client: HHClientPort) -> None:
        """Инициализация use case.

        Args:
            hh_client: HH клиент для выполнения запросов.
                      Может быть обычным клиентом или клиентом с автообновлением cookies.
        """
        self._hh_client = hh_client

    async def execute(
        self,
        chat_ids: List[int],
        headers: Dict[str, str],
        cookies: Dict[str, str],
    ) -> List[HHChatDetailed]:
        """Получить детальную информацию о чатах с сообщениями.

        Args:
            chat_ids: Список ID чатов для получения детальной информации.
            headers: HTTP заголовки для запросов к HH API.
            cookies: HTTP cookies для запросов к HH API.

        Returns:
            Список детальной информации о чатах (только успешно полученные).
        """
        # Параллельно получаем детальную информацию о каждом чате
        tasks = [
            self._hh_client.fetch_chat_detail(chat_id, headers, cookies)
            for chat_id in chat_ids
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Фильтруем только успешно полученные чаты
        chats: List[HHChatDetailed] = []
        for result in results:
            if isinstance(result, HHChatDetailed):
                chats.append(result)
            elif isinstance(result, Exception):
                logger.error(f"[fetch_chats_details] Ошибка получения чата: {result}")

        return chats

