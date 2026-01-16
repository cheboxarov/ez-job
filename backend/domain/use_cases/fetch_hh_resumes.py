"""Use case для получения списка резюме из HeadHunter."""

from __future__ import annotations

from typing import Dict, List

from domain.entities.hh_resume import HHResume
from domain.interfaces.hh_client_port import HHClientPort


class FetchHHResumesUseCase:
    """Use case для получения списка резюме пользователя из HeadHunter API."""

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
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
    ) -> List[HHResume]:
        """Получить список резюме из HeadHunter.

        Args:
            headers: Заголовки для запроса к HH API.
            cookies: Куки для запроса к HH API.
            internal_api_base_url: Базовый URL внутреннего API HH.

        Returns:
            Список резюме из HeadHunter.
        """
        return await self._hh_client.fetch_resumes(
            headers=headers,
            cookies=cookies,
            internal_api_base_url=internal_api_base_url,
        )

