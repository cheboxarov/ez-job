"""Use case для получения начальных куки для авторизации в HH."""

from __future__ import annotations

from typing import Dict

from loguru import logger

from domain.interfaces.hh_client_port import HHClientPort


class GetInitialCookiesUseCase:
    """Use case для получения начальных куки через GET запрос на /account/login."""

    def __init__(
        self,
        hh_client: HHClientPort,
    ) -> None:
        """Инициализация use case.

        Args:
            hh_client: Клиент для работы с HeadHunter API.
        """
        self._hh_client = hh_client

    async def execute(
        self,
        *,
        backurl: str = "",
        internal_api_base_url: str = "https://hh.ru",
    ) -> Dict[str, str]:
        """Получить начальные куки.

        Args:
            backurl: URL для редиректа после входа (опционально).
            internal_api_base_url: Базовый URL внутреннего API HH.

        Returns:
            Словарь с начальными куки.

        Raises:
            Exception: При ошибках выполнения запроса к HH API.
        """
        try:
            cookies = await self._hh_client.get_initial_cookies(
                backurl=backurl,
                internal_api_base_url=internal_api_base_url,
                return_cookies=False,
            )
            logger.info(f"Успешно получены начальные куки (количество: {len(cookies)})")
            return cookies
        except Exception as exc:
            logger.error(
                f"Ошибка при получении начальных куки: {exc}",
                exc_info=True,
            )
            raise

