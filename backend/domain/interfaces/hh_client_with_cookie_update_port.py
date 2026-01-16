"""Порт для HH клиента с автоматическим обновлением cookies."""

from __future__ import annotations

from domain.interfaces.hh_client_port import HHClientPort


class HHClientWithCookieUpdatePort(HHClientPort):
    """Порт для HH клиента с автоматическим обновлением cookies.
    
    Наследует все методы от HHClientPort и добавляет автоматическое
    обновление cookies после каждого запроса.
    
    Инфраструктура должна реализовать этот интерфейс.
    """
    pass
