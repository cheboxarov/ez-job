"""Use case для пометки сообщения в чате как прочитанного."""

from __future__ import annotations

from typing import Any, Dict

from domain.interfaces.hh_client_port import HHClientPort


class MarkChatMessageReadUseCase:
    """Use case для пометки сообщения в чате как прочитанного."""

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
        message_id: int,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        hhtm_source: str = "app",
        hhtm_source_label: str = "negotiation_list",
    ) -> Dict[str, Any]:
        """Пометить сообщение в чате как прочитанное.

        Args:
            chat_id: ID чата для пометки сообщения.
            message_id: ID сообщения для пометки как прочитанного.
            headers: HTTP заголовки для запросов к HH API.
            cookies: HTTP cookies для запросов к HH API.
            hhtm_source: Источник запроса (по умолчанию "app").
            hhtm_source_label: Метка источника (по умолчанию "negotiation_list").

        Returns:
            Ответ API с результатом пометки сообщения как прочитанного.
        """
        return await self._hh_client.mark_chat_message_read(
            chat_id=chat_id,
            message_id=message_id,
            headers=headers,
            cookies=cookies,
            hhtm_source=hhtm_source,
            hhtm_source_label=hhtm_source_label,
        )

