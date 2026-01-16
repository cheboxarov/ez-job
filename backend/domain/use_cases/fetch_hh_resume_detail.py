"""Use case для получения детального резюме из HeadHunter."""

from __future__ import annotations

from typing import Dict, Optional

from domain.entities.hh_resume_detailed import HHResumeDetailed
from domain.interfaces.hh_client_port import HHClientPort


class FetchHHResumeDetailUseCase:
    """Use case для получения детального резюме из HeadHunter API."""

    def __init__(self, hh_client: HHClientPort) -> None:
        """Инициализация use case.

        Args:
            hh_client: Клиент для работы с HeadHunter API.
                      Может быть обычным клиентом или клиентом с автообновлением cookies.
        """
        self._hh_client = hh_client

    async def execute(
        self,
        resume_hash: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
    ) -> Optional[HHResumeDetailed]:
        """Получить детальное резюме из HeadHunter.

        Args:
            resume_hash: Hash резюме из HeadHunter.
            headers: Заголовки для запроса к HH API.
            cookies: Куки для запроса к HH API.
            internal_api_base_url: Базовый URL внутреннего API HH.

        Returns:
            Детальное резюме из HeadHunter или None, если не найдено.
        """
        return await self._hh_client.fetch_resume_detail(
            resume_hash=resume_hash,
            headers=headers,
            cookies=cookies,
            internal_api_base_url=internal_api_base_url,
        )

