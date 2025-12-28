"""Реализация Unit of Work для управления транзакциями."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from domain.interfaces.unit_of_work_port import UnitOfWorkPort
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
from domain.interfaces.resume_to_vacancy_match_repository_port import (
    ResumeToVacancyMatchRepositoryPort,
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
from infrastructure.database.repositories.user_repository import UserRepository
from infrastructure.database.repositories.resume_filter_settings_repository import (
    ResumeFilterSettingsRepository,
)
from infrastructure.database.repositories.resume_repository import ResumeRepository
from infrastructure.database.repositories.user_hh_auth_data_repository import (
    UserHhAuthDataRepository,
)
from infrastructure.database.repositories.vacancy_response_repository import (
    VacancyResponseRepository,
)
from infrastructure.database.repositories.resume_to_vacancy_match_repository import (
    ResumeToVacancyMatchRepository,
)
from infrastructure.database.repositories.subscription_plan_repository import (
    SubscriptionPlanRepository,
)
from infrastructure.database.repositories.user_subscription_repository import (
    UserSubscriptionRepository,
)
from infrastructure.database.repositories.agent_action_repository import (
    AgentActionRepository,
)
from infrastructure.database.repositories.telegram_notification_settings_repository import (
    TelegramNotificationSettingsRepository,
)
from infrastructure.database.repositories.telegram_link_token_repository import (
    TelegramLinkTokenRepository,
)


class UnitOfWork(UnitOfWorkPort):
    """Реализация Unit of Work для управления транзакциями БД."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        """Инициализация Unit of Work.

        Args:
            session_factory: Фабрика для создания async сессий SQLAlchemy.
        """
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._user_repository: UserRepositoryPort | None = None
        self._resume_filter_settings_repository: ResumeFilterSettingsRepositoryPort | None = None
        self._resume_repository: ResumeRepositoryPort | None = None
        self._user_hh_auth_data_repository: UserHhAuthDataRepositoryPort | None = None
        self._vacancy_response_repository: VacancyResponseRepositoryPort | None = None
        self._resume_to_vacancy_match_repository: ResumeToVacancyMatchRepositoryPort | None = None
        self._subscription_plan_repository: SubscriptionPlanRepositoryPort | None = None
        self._user_subscription_repository: UserSubscriptionRepositoryPort | None = None
        self._agent_action_repository: AgentActionRepositoryPort | None = None
        self._telegram_notification_settings_repository: TelegramNotificationSettingsRepositoryPort | None = None
        self._telegram_link_token_repository: TelegramLinkTokenRepositoryPort | None = None

    @property
    def user_repository(self) -> UserRepositoryPort:
        """Получить репозиторий пользователя.

        Returns:
            Репозиторий пользователя.

        Raises:
            RuntimeError: Если UnitOfWork не был введен в контекст.
        """
        if self._user_repository is None:
            raise RuntimeError("UnitOfWork должен использоваться в async with контексте")
        return self._user_repository

    @property
    def resume_filter_settings_repository(self) -> ResumeFilterSettingsRepositoryPort:
        """Получить репозиторий настроек фильтров резюме.

        Returns:
            Репозиторий настроек фильтров резюме.

        Raises:
            RuntimeError: Если UnitOfWork не был введен в контекст.
        """
        if self._resume_filter_settings_repository is None:
            raise RuntimeError("UnitOfWork должен использоваться в async with контексте")
        return self._resume_filter_settings_repository

    @property
    def resume_repository(self) -> ResumeRepositoryPort:
        """Получить репозиторий резюме.

        Returns:
            Репозиторий резюме.

        Raises:
            RuntimeError: Если UnitOfWork не был введен в контекст.
        """
        if self._resume_repository is None:
            raise RuntimeError("UnitOfWork должен использоваться в async with контексте")
        return self._resume_repository

    @property
    def user_hh_auth_data_repository(self) -> UserHhAuthDataRepositoryPort:
        """Получить репозиторий HH auth data пользователя.

        Returns:
            Репозиторий HH auth data пользователя.

        Raises:
            RuntimeError: Если UnitOfWork не был введен в контекст.
        """
        if self._user_hh_auth_data_repository is None:
            raise RuntimeError("UnitOfWork должен использоваться в async with контексте")
        return self._user_hh_auth_data_repository

    @property
    def vacancy_response_repository(self) -> VacancyResponseRepositoryPort:
        """Получить репозиторий откликов на вакансии.

        Returns:
            Репозиторий откликов на вакансии.

        Raises:
            RuntimeError: Если UnitOfWork не был введен в контекст.
        """
        if self._vacancy_response_repository is None:
            raise RuntimeError("UnitOfWork должен использоваться в async with контексте")
        return self._vacancy_response_repository

    @property
    def resume_to_vacancy_match_repository(self) -> ResumeToVacancyMatchRepositoryPort:
        """Получить репозиторий мэтчей резюме-вакансия.

        Returns:
            Репозиторий мэтчей резюме-вакансия.

        Raises:
            RuntimeError: Если UnitOfWork не был введен в контекст.
        """
        if self._resume_to_vacancy_match_repository is None:
            raise RuntimeError("UnitOfWork должен использоваться в async with контексте")
        return self._resume_to_vacancy_match_repository

    @property
    def subscription_plan_repository(self) -> SubscriptionPlanRepositoryPort:
        """Получить репозиторий планов подписки.

        Returns:
            Репозиторий планов подписки.

        Raises:
            RuntimeError: Если UnitOfWork не был введен в контекст.
        """
        if self._subscription_plan_repository is None:
            raise RuntimeError("UnitOfWork должен использоваться в async with контексте")
        return self._subscription_plan_repository

    @property
    def user_subscription_repository(self) -> UserSubscriptionRepositoryPort:
        """Получить репозиторий подписок пользователей.

        Returns:
            Репозиторий подписок пользователей.

        Raises:
            RuntimeError: Если UnitOfWork не был введен в контекст.
        """
        if self._user_subscription_repository is None:
            raise RuntimeError("UnitOfWork должен использоваться в async with контексте")
        return self._user_subscription_repository

    @property
    def agent_action_repository(self) -> AgentActionRepositoryPort:
        """Получить репозиторий действий агента.

        Returns:
            Репозиторий действий агента.

        Raises:
            RuntimeError: Если UnitOfWork не был введен в контекст.
        """
        if self._agent_action_repository is None:
            raise RuntimeError("UnitOfWork должен использоваться в async with контексте")
        return self._agent_action_repository

    @property
    def telegram_notification_settings_repository(self) -> TelegramNotificationSettingsRepositoryPort:
        """Получить репозиторий настроек Telegram уведомлений.

        Returns:
            Репозиторий настроек Telegram уведомлений.

        Raises:
            RuntimeError: Если UnitOfWork не был введен в контекст.
        """
        if self._telegram_notification_settings_repository is None:
            raise RuntimeError("UnitOfWork должен использоваться в async with контексте")
        return self._telegram_notification_settings_repository

    @property
    def telegram_link_token_repository(self) -> TelegramLinkTokenRepositoryPort:
        """Получить репозиторий токенов привязки Telegram.

        Returns:
            Репозиторий токенов привязки Telegram.

        Raises:
            RuntimeError: Если UnitOfWork не был введен в контекст.
        """
        if self._telegram_link_token_repository is None:
            raise RuntimeError("UnitOfWork должен использоваться в async with контексте")
        return self._telegram_link_token_repository

    async def __aenter__(self) -> UnitOfWorkPort:
        """Вход в контекстный менеджер.

        Returns:
            Self для использования в async with.
        """
        self._session = self._session_factory()
        self._user_repository = UserRepository(self._session)
        self._resume_filter_settings_repository = ResumeFilterSettingsRepository(self._session)
        self._resume_repository = ResumeRepository(self._session)
        self._user_hh_auth_data_repository = UserHhAuthDataRepository(self._session)
        self._vacancy_response_repository = VacancyResponseRepository(self._session)
        self._resume_to_vacancy_match_repository = ResumeToVacancyMatchRepository(self._session)
        self._subscription_plan_repository = SubscriptionPlanRepository(self._session)
        self._user_subscription_repository = UserSubscriptionRepository(self._session)
        self._agent_action_repository = AgentActionRepository(self._session)
        self._telegram_notification_settings_repository = TelegramNotificationSettingsRepository(self._session)
        self._telegram_link_token_repository = TelegramLinkTokenRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Выход из контекстного менеджера.

        Args:
            exc_type: Тип исключения, если было.
            exc_val: Значение исключения, если было.
            exc_tb: Traceback исключения, если было.
        """
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

        if self._session:
            await self._session.close()

    async def commit(self) -> None:
        """Зафиксировать транзакцию."""
        if self._session:
            from loguru import logger
            logger.info("Коммит транзакции в UnitOfWork")
            await self._session.commit()
            logger.info("Транзакция успешно закоммичена")

    async def rollback(self) -> None:
        """Откатить транзакцию."""
        if self._session:
            await self._session.rollback()

