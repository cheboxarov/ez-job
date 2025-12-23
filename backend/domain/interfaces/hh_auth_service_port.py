"""Интерфейс сервиса авторизации HH."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict
from uuid import UUID

from domain.interfaces.unit_of_work_port import UnitOfWorkPort


class HhAuthServicePort(ABC):
    """Порт сервиса авторизации HH.

    Application слой должен реализовать этот интерфейс.
    Сервис оркестрирует use case'ы для авторизации в HH через OTP.
    """

    @abstractmethod
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

    @abstractmethod
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

