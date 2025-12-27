"""Use case для генерации OTP кода для авторизации в HH."""

from __future__ import annotations

from typing import Any, Dict, Optional

from loguru import logger

from application.utils.login_trust_flags_generator import generate_login_trust_flags
from domain.interfaces.hh_client_port import HHClientPort


class GenerateOtpUseCase:
    """Use case для запроса OTP кода на телефон для авторизации в HH."""

    def __init__(
        self,
        hh_client: HHClientPort,
        login_trust_flags_public_key: Optional[str] = None,
    ) -> None:
        """Инициализация use case.

        Args:
            hh_client: Клиент для работы с HeadHunter API.
            login_trust_flags_public_key: Публичный RSA ключ для генерации login_trust_flags.
        """
        self._hh_client = hh_client
        self._public_key = login_trust_flags_public_key

    async def execute(
        self,
        *,
        phone: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        internal_api_base_url: str = "https://hh.ru",
        login_trust_flags: Optional[str] = None,
        captcha: Optional[Dict[str, str]] = None,
    ) -> tuple[Dict[str, Any], Dict[str, str]]:
        """Запросить OTP код на телефон.

        Args:
            phone: Номер телефона в формате +7XXXXXXXXXX.
            headers: HTTP заголовки для запроса к HH API.
            cookies: HTTP cookies для запроса к HH API.
            internal_api_base_url: Базовый URL внутреннего API HH.
            login_trust_flags: Флаги доверия логина. Если None, генерируется динамически.

        Returns:
            Tuple с ответом от API HH и обновленными cookies.

        Raises:
            Exception: При ошибках выполнения запроса к HH API.
        """
        # Генерируем login_trust_flags, если не передан
        if login_trust_flags is None:
            if not self._public_key:
                raise ValueError("login_trust_flags не передан и публичный ключ не настроен")
            login_trust_flags = generate_login_trust_flags(self._public_key)

        try:
            result, updated_cookies = await self._hh_client.generate_otp(
                phone=phone,
                headers=headers,
                cookies=cookies,
                internal_api_base_url=internal_api_base_url,
                login_trust_flags=login_trust_flags,
                captcha=captcha,
                return_cookies=True,
            )
            logger.info(f"Успешно запрошен OTP код для телефона {phone}")
            return result, updated_cookies
        except Exception as exc:
            logger.error(
                f"Ошибка при запросе OTP кода для телефона {phone}: {exc}",
                exc_info=True,
            )
            raise

