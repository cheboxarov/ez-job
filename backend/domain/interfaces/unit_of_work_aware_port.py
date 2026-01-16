"""Интерфейс для сервисов, которые поддерживают установку UnitOfWork."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.interfaces.unit_of_work_port import UnitOfWorkPort


class UnitOfWorkAwarePort(ABC):
    """Порт для сервисов, которые могут использовать UnitOfWork для логирования.

    Используется для LLM-агентов и других сервисов, которым нужен доступ
    к UnitOfWork для логирования вызовов в БД.
    """

    @abstractmethod
    def set_unit_of_work(self, unit_of_work: "UnitOfWorkPort | None") -> None:
        """Установить UnitOfWork для логирования.

        Args:
            unit_of_work: UnitOfWork для логирования или None для отключения.
        """
