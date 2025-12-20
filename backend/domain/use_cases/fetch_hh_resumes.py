"""Use case для получения списка резюме из HeadHunter."""

from __future__ import annotations

from typing import Dict, List, Optional
from uuid import UUID

from domain.entities.hh_resume import HHResume
from domain.interfaces.hh_client_port import HHClientPort
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase
from infrastructure.clients.hh_client_with_cookie_update import HHHttpClientWithCookieUpdate


class FetchHHResumesUseCase:
    """Use case для получения списка резюме пользователя из HeadHunter API."""

    def __init__(self, hh_client: HHClientPort) -> None:
        """Инициализация use case.

        Args:
            hh_client: Клиент для работы с HeadHunter API.
        """
        self._hh_client = hh_client

    async def execute(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        user_id: Optional[UUID] = None,
        update_cookies_uc: Optional[UpdateUserHhAuthCookiesUseCase] = None,
    ) -> List[HHResume]:
        """Получить список резюме из HeadHunter.

        Args:
            headers: Заголовки для запроса к HH API.
            cookies: Куки для запроса к HH API.
            internal_api_base_url: Базовый URL внутреннего API HH.
            user_id: UUID пользователя для обновления cookies (опционально).
            update_cookies_uc: Use case для обновления cookies (опционально).

        Returns:
            Список резюме из HeadHunter.
        """
        # Если передан user_id и update_cookies_uc, используем обертку для автоматического сохранения cookies
        if user_id and update_cookies_uc:
            client = HHHttpClientWithCookieUpdate(self._hh_client, user_id, update_cookies_uc)
        else:
            client = self._hh_client
        return await client.fetch_resumes(
            headers=headers,
            cookies=cookies,
            internal_api_base_url=internal_api_base_url,
        )

