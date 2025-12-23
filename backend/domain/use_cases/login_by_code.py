"""Use case для входа в HH по OTP коду."""

from __future__ import annotations

from typing import Any, Dict, Optional

from loguru import logger

from application.utils.login_trust_flags_generator import generate_login_trust_flags
from domain.interfaces.hh_client_port import HHClientPort


class LoginByCodeUseCase:
    """Use case для входа в HH по OTP коду и получения cookies."""

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
        code: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        internal_api_base_url: str = "https://novosibirsk.hh.ru",
        backurl: str = "",
        remember: bool = True,
        login_trust_flags: Optional[str] = None,
    ) -> tuple[Dict[str, Any], Dict[str, str]]:
        """Войти по OTP коду и получить cookies.

        Args:
            phone: Номер телефона в формате +7XXXXXXXXXX.
            code: OTP код из SMS.
            headers: HTTP заголовки для запроса к HH API.
            cookies: HTTP cookies для запроса к HH API.
            internal_api_base_url: Базовый URL внутреннего API HH.
            backurl: URL для редиректа после входа.
            remember: Запомнить пользователя.
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
            result, updated_cookies = await self._hh_client.login_by_code(
                phone=phone,
                code=code,
                headers=headers,
                cookies=cookies,
                internal_api_base_url=internal_api_base_url,
                backurl=backurl,
                remember=remember,
                login_trust_flags=login_trust_flags,
                return_cookies=True,
            )
            logger.info(
                f"Успешный вход по OTP коду для телефона {phone}. "
                f"Получено cookies: {len(updated_cookies)} ключей"
            )
            return result, updated_cookies
        except Exception as exc:
            logger.error(
                f"Ошибка при входе по OTP коду для телефона {phone}: {exc}",
                exc_info=True,
            )
            raise

