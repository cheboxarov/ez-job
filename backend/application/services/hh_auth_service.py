"""Сервис приложения для авторизации в HH через OTP."""

from __future__ import annotations

from typing import Any, Dict

from domain.interfaces.hh_auth_service_port import HhAuthServicePort
from domain.use_cases.generate_otp import GenerateOtpUseCase
from domain.use_cases.get_initial_cookies import GetInitialCookiesUseCase
from domain.use_cases.login_by_code import LoginByCodeUseCase
from infrastructure.clients.hh_client import HHHttpClient


class HhAuthService(HhAuthServicePort):
    """Сервис для авторизации в HH через OTP, оркестрирующий use case'ы."""

    def __init__(
        self,
        hh_client: HHHttpClient,
        login_trust_flags_public_key: str | None = None,
    ) -> None:
        """Инициализация сервиса.

        Args:
            hh_client: Клиент для работы с HeadHunter API.
            login_trust_flags_public_key: Публичный RSA ключ для генерации login_trust_flags.
        """
        self._hh_client = hh_client
        self._public_key = login_trust_flags_public_key
        self._get_initial_cookies_uc = GetInitialCookiesUseCase(hh_client)
        self._generate_otp_uc = GenerateOtpUseCase(
            hh_client, login_trust_flags_public_key=login_trust_flags_public_key
        )
        self._login_by_code_uc = LoginByCodeUseCase(
            hh_client, login_trust_flags_public_key=login_trust_flags_public_key
        )

    async def generate_otp(
        self,
        phone: str,
        *,
        cookies: Dict[str, str] | None = None,
        captcha: Dict[str, str] | None = None,
    ) -> tuple[Dict[str, Any], Dict[str, str]]:
        """Запросить OTP код на телефон.

        Args:
            phone: Номер телефона в формате +7XXXXXXXXXX.

        Returns:
            Tuple с результатом запроса и промежуточными cookies.

        Raises:
            Exception: При ошибках выполнения запроса к HH API.
        """
        # Расширенные headers для имитации браузера (как в app.py)
        headers: Dict[str, str] = {
            "accept": "application/json",
            "accept-language": "ru-RU,ru;q=0.9",
            "origin": "https://hh.ru",
            "referer": "https://hh.ru/account/login?role=applicant&backurl=%2F&hhtmFrom=vacancy",
            "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }

        # Если cookies не переданы с фронта, получаем начальные куки динамически
        if cookies is None:
            cookies = await self._get_initial_cookies_uc.execute(
                backurl="/",
                internal_api_base_url="https://hh.ru",
            )

        # Вызываем use case
        result, updated_cookies = await self._generate_otp_uc.execute(
            phone=phone,
            headers=headers,
            cookies=cookies,
            internal_api_base_url="https://hh.ru",
            captcha=captcha,
        )

        return result, updated_cookies

    async def login_by_code(
        self,
        phone: str,
        code: str,
        cookies: Dict[str, str],
    ) -> tuple[Dict[str, str], Dict[str, str]]:
        """Войти по OTP коду и получить финальные headers/cookies.

        Args:
            phone: Номер телефона в формате +7XXXXXXXXXX.
            code: OTP код из SMS.
            cookies: Промежуточные cookies из предыдущего шага (generate_otp).

        Returns:
            Кортеж (headers, final_cookies) после успешного входа.

        Raises:
            Exception: При ошибках выполнения запроса к HH API или сохранения в БД.
        """
        # Расширенные headers (как в app.py)
        headers: Dict[str, str] = {
            "accept": "application/json",
            "accept-language": "ru-RU,ru;q=0.9",
            "origin": "https://novosibirsk.hh.ru",
            "referer": "https://novosibirsk.hh.ru/account/login?role=applicant&backurl=%2F&hhtmFrom=main",
            "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }

        # Используем промежуточные cookies от клиента и вызываем use case
        _result, final_cookies = await self._login_by_code_uc.execute(
            phone=phone,
            code=code,
            headers=headers,
            cookies=cookies,
        )
        return headers, final_cookies

    async def get_captcha_key(
        self,
        cookies: Dict[str, str],
        lang: str = "RU",
    ) -> tuple[Dict[str, Any], Dict[str, str]]:
        """Получить ключ капчи HH.

        Args:
            cookies: Текущие cookies HH.
            lang: Язык капчи (по умолчанию RU).

        Returns:
            Tuple с результатом (содержит ключ капчи) и обновленными cookies.

        Raises:
            Exception: При ошибках выполнения запроса к HH API.
        """
        # Расширенные headers для имитации браузера
        headers: Dict[str, str] = {
            "accept": "application/json",
            "accept-language": "ru-RU,ru;q=0.9",
            "origin": "https://hh.ru",
            "referer": "https://hh.ru/account/login?role=applicant&backurl=%2F&hhtmFrom=vacancy",
            "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }

        result, updated_cookies = await self._hh_client.get_captcha_key(
            headers=headers,
            cookies=cookies,
            lang=lang,
            internal_api_base_url="https://hh.ru",
            return_cookies=True,
        )
        return result, updated_cookies

    async def get_captcha_picture(
        self,
        cookies: Dict[str, str],
        captcha_key: str,
    ) -> tuple[Dict[str, Any], Dict[str, str]]:
        """Получить картинку капчи HH в base64.

        Args:
            cookies: Текущие cookies HH.
            captcha_key: Ключ капчи, полученный из get_captcha_key.

        Returns:
            Tuple с результатом (содержит content_type и image_base64) и обновленными cookies.

        Raises:
            Exception: При ошибках выполнения запроса к HH API.
        """
        # Расширенные headers для имитации браузера
        headers: Dict[str, str] = {
            "accept": "application/json",
            "accept-language": "ru-RU,ru;q=0.9",
            "origin": "https://hh.ru",
            "referer": "https://hh.ru/account/login?role=applicant&backurl=%2F&hhtmFrom=vacancy",
            "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }

        result, updated_cookies = await self._hh_client.get_captcha_picture(
            headers=headers,
            cookies=cookies,
            captcha_key=captcha_key,
            internal_api_base_url="https://hh.ru",
            return_cookies=True,
        )
        return result, updated_cookies
