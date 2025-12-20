"""Use case для получения детального резюме из HeadHunter."""

from __future__ import annotations

from typing import Dict, Optional
from uuid import UUID

from domain.entities.hh_resume_detailed import HHResumeDetailed
from domain.interfaces.hh_client_port import HHClientPort
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase
from infrastructure.clients.hh_client_with_cookie_update import HHHttpClientWithCookieUpdate


class FetchHHResumeDetailUseCase:
    """Use case для получения детального резюме из HeadHunter API."""

    def __init__(self, hh_client: HHClientPort) -> None:
        """Инициализация use case.

        Args:
            hh_client: Клиент для работы с HeadHunter API.
        """
        self._hh_client = hh_client

    async def execute(
        self,
        resume_hash: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        user_id: Optional[UUID] = None,
        update_cookies_uc: Optional[UpdateUserHhAuthCookiesUseCase] = None,
    ) -> Optional[HHResumeDetailed]:
        """Получить детальное резюме из HeadHunter.

        Args:
            resume_hash: Hash резюме из HeadHunter.
            headers: Заголовки для запроса к HH API.
            cookies: Куки для запроса к HH API.
            internal_api_base_url: Базовый URL внутреннего API HH.
            user_id: UUID пользователя для обновления cookies (опционально).
            update_cookies_uc: Use case для обновления cookies (опционально).

        Returns:
            Детальное резюме из HeadHunter или None, если не найдено.
        """
        # Если передан user_id и update_cookies_uc, используем обертку для автоматического сохранения cookies
        if user_id and update_cookies_uc:
            client = HHHttpClientWithCookieUpdate(self._hh_client, user_id, update_cookies_uc)
        else:
            client = self._hh_client
        return await client.fetch_resume_detail(
            resume_hash=resume_hash,
            headers=headers,
            cookies=cookies,
            internal_api_base_url=internal_api_base_url,
        )

