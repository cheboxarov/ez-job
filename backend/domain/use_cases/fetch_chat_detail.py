"""Use case для получения детальной информации об одном чате."""

from __future__ import annotations

from typing import Dict, Optional

from domain.entities.hh_chat_detailed import HHChatDetailed
from domain.interfaces.hh_client_port import HHClientPort


class FetchChatDetailUseCase:
    """Use case получения детальной информации об одном чате с сообщениями."""

    def __init__(self, hh_client: HHClientPort) -> None:
        """Инициализация use case.

        Args:
            hh_client: HH клиент для выполнения запросов.
                      Может быть обычным клиентом или клиентом с автообновлением cookies.
        """
        self._hh_client = hh_client

    async def execute(
        self,
        chat_id: int,
        headers: Dict[str, str],
        cookies: Dict[str, str],
    ) -> Optional[HHChatDetailed]:
        """Получить детальную информацию об одном чате с сообщениями.

        Args:
            chat_id: ID чата для получения детальной информации.
            headers: HTTP заголовки для запросов к HH API.
            cookies: HTTP cookies для запросов к HH API.

        Returns:
            Детальная информация о чате или None, если чат не найден.
        """
        return await self._hh_client.fetch_chat_detail(
            chat_id=chat_id,
            headers=headers,
            cookies=cookies,
        )

