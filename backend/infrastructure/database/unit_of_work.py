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
from domain.interfaces.llm_call_repository_port import (
    LlmCallRepositoryPort,
)
from domain.interfaces.user_automation_settings_repository_port import (
    UserAutomationSettingsRepositoryPort,
)
from domain.interfaces.resume_evaluation_repository_port import (
    ResumeEvaluationRepositoryPort,
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
from infrastructure.database.repositories.llm_call_repository import (
    LlmCallRepository,
)
from infrastructure.database.repositories.user_automation_settings_repository import (
    UserAutomationSettingsRepository,
)
from infrastructure.database.repositories.resume_evaluation_repository import (
    ResumeEvaluationRepository,
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
        # Транзакционные репозитории (одна сессия на все)
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
        self._llm_call_repository: LlmCallRepositoryPort | None = None
        self._user_automation_settings_repository: UserAutomationSettingsRepositoryPort | None = None
        self._resume_evaluation_repository: ResumeEvaluationRepositoryPort | None = None
        # Кеш для standalone репозиториев
        self._standalone_repositories: dict[str, any] = {}

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

    @property
    def llm_call_repository(self) -> LlmCallRepositoryPort:
        """Получить репозиторий для логирования вызовов LLM.

        Returns:
            Репозиторий для логирования вызовов LLM.

        Raises:
            RuntimeError: Если UnitOfWork не был введен в контекст.
        """
        if self._llm_call_repository is None:
            raise RuntimeError("UnitOfWork должен использоваться в async with контексте")
        return self._llm_call_repository

    @property
    def user_automation_settings_repository(self) -> UserAutomationSettingsRepositoryPort:
        """Получить репозиторий настроек автоматизации пользователя.

        Returns:
            Репозиторий настроек автоматизации пользователя.

        Raises:
            RuntimeError: Если UnitOfWork не был введен в контекст.
        """
        if self._user_automation_settings_repository is None:
            raise RuntimeError("UnitOfWork должен использоваться в async with контексте")
        return self._user_automation_settings_repository

    @property
    def resume_evaluation_repository(self) -> ResumeEvaluationRepositoryPort:
        """Получить репозиторий оценок резюме.

        Returns:
            Репозиторий оценок резюме.

        Raises:
            RuntimeError: Если UnitOfWork не был введен в контекст.
        """
        if self._resume_evaluation_repository is None:
            raise RuntimeError("UnitOfWork должен использоваться в async with контексте")
        return self._resume_evaluation_repository

    # ========== Standalone репозитории (неатомарные операции) ==========

    @property
    def standalone_user_repository(self) -> UserRepositoryPort:
        """Получить standalone репозиторий пользователя.
        
        Каждый вызов метода создает свою сессию и коммитит отдельно.
        Используется для операций, которые не требуют атомарности.
        """
        if "user" not in self._standalone_repositories:
            self._standalone_repositories["user"] = UserRepository(self._session_factory)
        return self._standalone_repositories["user"]

    @property
    def standalone_resume_filter_settings_repository(self) -> ResumeFilterSettingsRepositoryPort:
        """Получить standalone репозиторий настроек фильтров резюме."""
        if "resume_filter_settings" not in self._standalone_repositories:
            self._standalone_repositories["resume_filter_settings"] = ResumeFilterSettingsRepository(self._session_factory)
        return self._standalone_repositories["resume_filter_settings"]

    @property
    def standalone_resume_repository(self) -> ResumeRepositoryPort:
        """Получить standalone репозиторий резюме."""
        if "resume" not in self._standalone_repositories:
            self._standalone_repositories["resume"] = ResumeRepository(self._session_factory)
        return self._standalone_repositories["resume"]

    @property
    def standalone_user_hh_auth_data_repository(self) -> UserHhAuthDataRepositoryPort:
        """Получить standalone репозиторий HH auth data пользователя."""
        if "user_hh_auth_data" not in self._standalone_repositories:
            self._standalone_repositories["user_hh_auth_data"] = UserHhAuthDataRepository(self._session_factory)
        return self._standalone_repositories["user_hh_auth_data"]

    @property
    def standalone_vacancy_response_repository(self) -> VacancyResponseRepositoryPort:
        """Получить standalone репозиторий откликов на вакансии."""
        if "vacancy_response" not in self._standalone_repositories:
            self._standalone_repositories["vacancy_response"] = VacancyResponseRepository(self._session_factory)
        return self._standalone_repositories["vacancy_response"]

    @property
    def standalone_resume_to_vacancy_match_repository(self) -> ResumeToVacancyMatchRepositoryPort:
        """Получить standalone репозиторий мэтчей резюме-вакансия."""
        if "resume_to_vacancy_match" not in self._standalone_repositories:
            self._standalone_repositories["resume_to_vacancy_match"] = ResumeToVacancyMatchRepository(self._session_factory)
        return self._standalone_repositories["resume_to_vacancy_match"]

    @property
    def standalone_subscription_plan_repository(self) -> SubscriptionPlanRepositoryPort:
        """Получить standalone репозиторий планов подписки."""
        if "subscription_plan" not in self._standalone_repositories:
            self._standalone_repositories["subscription_plan"] = SubscriptionPlanRepository(self._session_factory)
        return self._standalone_repositories["subscription_plan"]

    @property
    def standalone_user_subscription_repository(self) -> UserSubscriptionRepositoryPort:
        """Получить standalone репозиторий подписок пользователей."""
        if "user_subscription" not in self._standalone_repositories:
            self._standalone_repositories["user_subscription"] = UserSubscriptionRepository(self._session_factory)
        return self._standalone_repositories["user_subscription"]

    @property
    def standalone_agent_action_repository(self) -> AgentActionRepositoryPort:
        """Получить standalone репозиторий действий агента."""
        if "agent_action" not in self._standalone_repositories:
            self._standalone_repositories["agent_action"] = AgentActionRepository(self._session_factory)
        return self._standalone_repositories["agent_action"]

    @property
    def standalone_telegram_notification_settings_repository(self) -> TelegramNotificationSettingsRepositoryPort:
        """Получить standalone репозиторий настроек Telegram уведомлений."""
        if "telegram_notification_settings" not in self._standalone_repositories:
            self._standalone_repositories["telegram_notification_settings"] = TelegramNotificationSettingsRepository(self._session_factory)
        return self._standalone_repositories["telegram_notification_settings"]

    @property
    def standalone_telegram_link_token_repository(self) -> TelegramLinkTokenRepositoryPort:
        """Получить standalone репозиторий токенов привязки Telegram."""
        if "telegram_link_token" not in self._standalone_repositories:
            self._standalone_repositories["telegram_link_token"] = TelegramLinkTokenRepository(self._session_factory)
        return self._standalone_repositories["telegram_link_token"]

    @property
    def standalone_llm_call_repository(self) -> LlmCallRepositoryPort:
        """Получить standalone репозиторий для логирования вызовов LLM."""
        if "llm_call" not in self._standalone_repositories:
            self._standalone_repositories["llm_call"] = LlmCallRepository(self._session_factory)
        return self._standalone_repositories["llm_call"]

    @property
    def standalone_user_automation_settings_repository(self) -> UserAutomationSettingsRepositoryPort:
        """Получить standalone репозиторий настроек автоматизации пользователя."""
        if "user_automation_settings" not in self._standalone_repositories:
            self._standalone_repositories["user_automation_settings"] = UserAutomationSettingsRepository(self._session_factory)
        return self._standalone_repositories["user_automation_settings"]

    @property
    def standalone_resume_evaluation_repository(self) -> ResumeEvaluationRepositoryPort:
        """Получить standalone репозиторий оценок резюме."""
        if "resume_evaluation" not in self._standalone_repositories:
            self._standalone_repositories["resume_evaluation"] = ResumeEvaluationRepository(self._session_factory)
        return self._standalone_repositories["resume_evaluation"]

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
        self._llm_call_repository = LlmCallRepository(self._session)
        self._user_automation_settings_repository = UserAutomationSettingsRepository(self._session)
        self._resume_evaluation_repository = ResumeEvaluationRepository(self._session)
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
        
        # Очищаем кеш standalone репозиториев
        self._standalone_repositories.clear()

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

