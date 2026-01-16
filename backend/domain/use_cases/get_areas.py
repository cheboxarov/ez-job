from __future__ import annotations

from typing import Any, Dict, List

from domain.interfaces.hh_client_port import HHClientPort


class GetAreasUseCase:
    """Use case для получения дерева регионов из HH API."""

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
    ) -> List[Dict[str, Any]]:
        """Возвращает дерево регионов как есть из публичного API /areas.

        Args:
            headers: HTTP заголовки для запроса к HH API.
            cookies: HTTP cookies для запроса к HH API.

        Returns:
            Дерево регионов из HH API.
        """
        return await self._hh_client.fetch_areas(headers, cookies)

