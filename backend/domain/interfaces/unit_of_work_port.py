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
from domain.interfaces.subscription_plan_repository_port import (
    SubscriptionPlanRepositoryPort,
)
from domain.interfaces.user_subscription_repository_port import (
    UserSubscriptionRepositoryPort,
)
from domain.interfaces.agent_action_repository_port import (
    AgentActionRepositoryPort,
)
from domain.interfaces.telegram_notification_settings_repository_port import (
    TelegramNotificationSettingsRepositoryPort,
)
from domain.interfaces.telegram_link_token_repository_port import (
    TelegramLinkTokenRepositoryPort,
)
from domain.interfaces.llm_call_repository_port import (
    LlmCallRepositoryPort,
)
from domain.interfaces.user_automation_settings_repository_port import (
    UserAutomationSettingsRepositoryPort,
)
from domain.interfaces.resume_evaluation_repository_port import (
    ResumeEvaluationRepositoryPort,
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

    @property
    @abstractmethod
    def subscription_plan_repository(self) -> SubscriptionPlanRepositoryPort:
        """Получить репозиторий планов подписки."""

    @property
    @abstractmethod
    def user_subscription_repository(self) -> UserSubscriptionRepositoryPort:
        """Получить репозиторий подписок пользователей."""

    @property
    @abstractmethod
    def agent_action_repository(self) -> AgentActionRepositoryPort:
        """Получить репозиторий действий агента."""

    @property
    @abstractmethod
    def telegram_notification_settings_repository(self) -> TelegramNotificationSettingsRepositoryPort:
        """Получить репозиторий настроек Telegram уведомлений."""

    @property
    @abstractmethod
    def telegram_link_token_repository(self) -> TelegramLinkTokenRepositoryPort:
        """Получить репозиторий токенов привязки Telegram."""

    @property
    @abstractmethod
    def llm_call_repository(self) -> LlmCallRepositoryPort:
        """Получить репозиторий для логирования вызовов LLM."""

    @property
    @abstractmethod
    def user_automation_settings_repository(self) -> UserAutomationSettingsRepositoryPort:
        """Получить репозиторий настроек автоматизации пользователя."""

    @property
    @abstractmethod
    def resume_evaluation_repository(self) -> ResumeEvaluationRepositoryPort:
        """Получить репозиторий оценок резюме."""

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

