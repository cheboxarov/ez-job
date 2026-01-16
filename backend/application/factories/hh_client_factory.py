"""Фабрика для создания HH клиентов."""

from __future__ import annotations

from uuid import UUID

from config import HHConfig
from domain.interfaces.hh_client_port import HHClientPort
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase
from infrastructure.clients.hh_client import HHHttpClient
from infrastructure.clients.hh_client_with_cookie_update import HHHttpClientWithCookieUpdate


def create_hh_client(config: HHConfig) -> HHClientPort:
    """Создаёт базовый HH клиент.

    Args:
        config: Конфигурация HH API.

    Returns:
        Базовый HH клиент без автоматического обновления cookies.
    """
    return HHHttpClient(config)


def create_hh_client_with_cookie_update(
    config: HHConfig,
    user_id: UUID,
    update_cookies_uc: UpdateUserHhAuthCookiesUseCase,
) -> HHClientPort:
    """Создаёт HH клиент с автоматическим обновлением cookies.

    Args:
        config: Конфигурация HH API.
        user_id: UUID пользователя, для которого обновляются cookies.
        update_cookies_uc: Use case для обновления cookies в БД.

    Returns:
        HH клиент с автоматическим обновлением cookies после каждого запроса.
    """
    base_client = HHHttpClient(config)
    return HHHttpClientWithCookieUpdate(base_client, user_id, update_cookies_uc)
