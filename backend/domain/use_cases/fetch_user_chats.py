from __future__ import annotations

from typing import Dict

from domain.entities.hh_list_chat import HHListChat
from domain.interfaces.hh_client_port import HHClientPort


class FetchUserChatsUseCase:
    """Use case получения списка чатов пользователя."""

    def __init__(self, hh_client: HHClientPort) -> None:
        """Инициализация use case.

        Args:
            hh_client: Клиент для работы с HeadHunter API.
                      Может быть обычным клиентом или клиентом с автообновлением cookies.
        """
        self._hh_client = hh_client

    async def execute(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
    ) -> HHListChat:
        """Получить список всех чатов пользователя.

        Args:
            headers: HTTP заголовки для запросов к HH API.
            cookies: HTTP cookies для запросов к HH API.

        Returns:
            Список чатов пользователя.
        """
        # Вызываем fetch_chat_list с пустым списком ID для получения всех чатов
        result = await self._hh_client.fetch_chat_list(
            chat_ids=[],
            headers=headers,
            cookies=cookies,
            filter_unread=True,
        )

        return result

