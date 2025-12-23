"""Сервис приложения для авторизации в HH через OTP."""

from __future__ import annotations

from typing import Any, Dict
from uuid import UUID

from domain.interfaces.hh_auth_service_port import HhAuthServicePort
from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from domain.use_cases.generate_otp import GenerateOtpUseCase
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
        self._generate_otp_uc = GenerateOtpUseCase(
            hh_client, login_trust_flags_public_key=login_trust_flags_public_key
        )
        self._login_by_code_uc = LoginByCodeUseCase(
            hh_client, login_trust_flags_public_key=login_trust_flags_public_key
        )

    async def generate_otp(
        self,
        phone: str,
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

        # Начальные cookies для обхода защиты (как в app.py)
        # Эти cookies нужны для первого запроса, чтобы не получить 403
        cookies: Dict[str, str] = {
            "__ddg1_": "UMP1V9ij9Yq7rMoKg1Tw",
            "hhrole": "anonymous",
            "regions": "4",
            "_xsrf": "33c9bdf68f58f5e61dc099099fd88e9f",
            "hhtoken": "tpQMTjX2KRMzquBiMZyGh0tHDnbG",
            "hhuid": "hV7IbHYj1pENjmlIcK43OA--",
            "__ddg9_": "147.45.139.118",
            "__zzatgib-w-hh": "MDA0dC0jViV+FmELHw4/aQsbSl1pCENQGC9LXy9ecGlPZ3gSUURcCTIsHRR5aysKf0AVQUFxL1xwIiBoOVURCxIXRF5cVWl1FRpLSiVueCplJS0xViR8SylEXFN/KB4WeHEqUQsNVy8NPjteLW8PJwsSWAkhCklpC15MDfb2SA==",
            "gsscgib-w-hh": "jEM8ZvjeDzf1NnISyM7guHn3N2Qjej8N0ajJcZ0kBLrnPv/t+UVFUmSljlb7RQPaY02rcTimxuMmE1kCUrZcKRZTtPt95bYVZVSsS4E+C9EiaP7FYKpKWfQA8Ddt7QHFBSgmWjV8dgHZN2clYoRWJ2iu2oD8pZf6p91ouY47KUn6QwMnxwcGPxHWYI3mNpptRC+ohahB3DsUjkf4b1/e/4RUN2ZBXii3qZIycRCL4LQQixxg7AQ8JcjxO43/66Lxtbq6TncYmRefaPk=",
            "fgsscgib-w-hh": "DWHr9723415842cd920b000cbb10a898d9b9d2cf",
        }

        # Вызываем use case
        result, updated_cookies = await self._generate_otp_uc.execute(
            phone=phone,
            headers=headers,
            cookies=cookies,
        )

        return result, updated_cookies

    async def login_by_code(
        self,
        user_id: UUID,
        phone: str,
        code: str,
        cookies: Dict[str, str],
        unit_of_work: UnitOfWorkPort,
    ) -> Dict[str, str]:
        """Войти по OTP коду и сохранить cookies в БД.

        Args:
            user_id: UUID пользователя.
            phone: Номер телефона в формате +7XXXXXXXXXX.
            code: OTP код из SMS.
            cookies: Промежуточные cookies из предыдущего шага (generate_otp).
            unit_of_work: UnitOfWork для сохранения данных в БД.

        Returns:
            Словарь с финальными cookies после успешного входа.

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

        # Используем промежуточные cookies от клиента
        # Вызываем use case
        result, final_cookies = await self._login_by_code_uc.execute(
            phone=phone,
            code=code,
            headers=headers,
            cookies=cookies,
        )

        # Сохраняем финальные cookies в БД
        await unit_of_work.user_hh_auth_data_repository.upsert(
            user_id=user_id,
            headers=headers,
            cookies=final_cookies,
        )
        await unit_of_work.commit()

        return final_cookies

