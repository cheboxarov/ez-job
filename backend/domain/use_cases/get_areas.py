from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from domain.interfaces.hh_client_port import HHClientPort
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase
from infrastructure.clients.hh_client_with_cookie_update import HHHttpClientWithCookieUpdate


class GetAreasUseCase:
    """Use case для получения дерева регионов из HH API."""

    def __init__(self, hh_client: HHClientPort) -> None:
        self._hh_client = hh_client

    async def execute(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        user_id: Optional[UUID] = None,
        update_cookies_uc: Optional[UpdateUserHhAuthCookiesUseCase] = None,
    ) -> List[Dict[str, Any]]:
        """Возвращает дерево регионов как есть из публичного API /areas."""
        # Если передан user_id и update_cookies_uc, используем обертку для автоматического сохранения cookies
        if user_id and update_cookies_uc:
            client = HHHttpClientWithCookieUpdate(self._hh_client, user_id, update_cookies_uc)
        else:
            client = self._hh_client
        return await client.fetch_areas(headers, cookies)

