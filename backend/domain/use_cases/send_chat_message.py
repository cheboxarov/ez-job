"""Use case для отправки сообщения в чат."""

from __future__ import annotations

from typing import Any, Dict, Optional

from domain.interfaces.hh_client_port import HHClientPort


class SendChatMessageUseCase:
    """Use case для отправки сообщения в чат."""

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
        text: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        idempotency_key: Optional[str] = None,
        hhtm_source: str = "app",
        hhtm_source_label: str = "chat",
    ) -> Dict[str, Any]:
        """Отправить сообщение в чат.

        Args:
            chat_id: ID чата для отправки сообщения.
            text: Текст сообщения для отправки.
            headers: HTTP заголовки для запросов к HH API.
            cookies: HTTP cookies для запросов к HH API.
            idempotency_key: Ключ идемпотентности (опционально).
            hhtm_source: Источник запроса (по умолчанию "app").
            hhtm_source_label: Метка источника (по умолчанию "chat").

        Returns:
            Ответ API с результатом отправки сообщения.
        """
        return await self._hh_client.send_chat_message(
            chat_id=chat_id,
            text=text,
            headers=headers,
            cookies=cookies,
            idempotency_key=idempotency_key,
            hhtm_source=hhtm_source,
            hhtm_source_label=hhtm_source_label,
        )

