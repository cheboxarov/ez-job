"""Интерфейс Unit of Work для управления транзакциями."""

from __future__ import annotations

from abc import ABC, abstractmethod

from domain.interfaces.user_repository_port import UserRepositoryPort
from domain.interfaces.resume_filter_settings_repository_port import (
    ResumeFilterSettingsRepositoryPort,
)
from domain.interfaces.resume_repository_port import ResumeRepositoryPort
from domain.interfaces.user_hh_auth_data_repository_port import (
    UserHhAuthDataRepositoryPort,
)
from domain.interfaces.vacancy_response_repository_port import (
    VacancyResponseRepositoryPort,
)


class UnitOfWorkPort(ABC):
    """Порт Unit of Work для управления транзакциями БД.

    Паттерн Unit of Work позволяет группировать несколько операций
    в одну транзакцию. Инфраструктура должна реализовать этот интерфейс.
    """

    @property
    @abstractmethod
    def user_repository(self) -> UserRepositoryPort:
        """Получить репозиторий пользователя.

        Returns:
            Репозиторий пользователя.
        """

    @property
    @abstractmethod
    def resume_filter_settings_repository(self) -> ResumeFilterSettingsRepositoryPort:
        """Получить репозиторий настроек фильтров резюме."""

    @property
    @abstractmethod
    def resume_repository(self) -> ResumeRepositoryPort:
        """Получить репозиторий резюме."""

    @property
    @abstractmethod
    def user_hh_auth_data_repository(self) -> UserHhAuthDataRepositoryPort:
        """Получить репозиторий HH auth data пользователя."""

    @property
    @abstractmethod
    def vacancy_response_repository(self) -> VacancyResponseRepositoryPort:
        """Получить репозиторий откликов на вакансии."""

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWorkPort":
        """Вход в контекстный менеджер.

        Returns:
            Self для использования в async with.
        """

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Выход из контекстного менеджера.

        Args:
            exc_type: Тип исключения, если было.
            exc_val: Значение исключения, если было.
            exc_tb: Traceback исключения, если было.
        """

    @abstractmethod
    async def commit(self) -> None:
        """Зафиксировать транзакцию."""

    @abstractmethod
    async def rollback(self) -> None:
        """Откатить транзакцию."""

