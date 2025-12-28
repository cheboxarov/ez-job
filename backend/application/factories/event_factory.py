"""Фабрика для создания зависимостей событий."""

from __future__ import annotations

from functools import lru_cache

from config import AppConfig, load_config
from infrastructure.events.event_bus import EventBus
from infrastructure.events.event_publisher import EventPublisher
from loguru import logger


# Singleton Event Bus для всего приложения
_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Возвращает singleton Event Bus.
    
    Returns:
        Singleton экземпляр Event Bus.
    """
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


def create_event_publisher(config: AppConfig | None = None) -> EventPublisher:
    """Создаёт EventPublisher с singleton Event Bus и опциональной поддержкой Telegram.
    
    Args:
        config: Конфигурация приложения. Если None, загружается автоматически.
    
    Returns:
        Экземпляр EventPublisher.
    """
    telegram_notification_uc = None
    
    if config is None:
        config = load_config()
    
    # Создаём Telegram notification use case, если Telegram настроен
    if config.telegram.bot_token:
        try:
            from domain.use_cases.send_telegram_notification import (
                SendTelegramNotificationUseCase,
            )
            from infrastructure.database.session import create_session_factory
            from infrastructure.database.repositories.telegram_notification_settings_repository import (
                TelegramNotificationSettingsRepository,
            )
            from infrastructure.telegram.telegram_bot import TelegramBot
            from infrastructure.telegram.telegram_notification_formatter import (
                TelegramNotificationFormatter,
            )
            
            session_factory = create_session_factory(config.database)
            telegram_bot = TelegramBot(
                bot_token=config.telegram.bot_token,
                link_token_handler=None,  # Устанавливается при запуске приложения
                unlink_handler=None,  # Устанавливается при запуске приложения
            )
            formatter = TelegramNotificationFormatter(frontend_url=config.telegram.frontend_url)
            
            # Создаём use case с функцией для получения репозитория из сессии
            async def get_repository():
                async with session_factory() as session:
                    return TelegramNotificationSettingsRepository(session)
            
            # Для EventPublisher нужен синхронный способ получения репозитория
            # Поэтому создаём use case, который будет создавать репозиторий при каждом вызове
            class TelegramNotificationUseCaseWrapper:
                def __init__(self, session_factory, telegram_bot, formatter):
                    self._session_factory = session_factory
                    self._telegram_bot = telegram_bot
                    self._formatter = formatter
                
                async def execute_for_agent_action(self, action):
                    from domain.use_cases.send_telegram_notification import (
                        SendTelegramNotificationUseCase,
                    )
                    from infrastructure.database.repositories.telegram_notification_settings_repository import (
                        TelegramNotificationSettingsRepository,
                    )
                    
                    async with self._session_factory() as session:
                        repository = TelegramNotificationSettingsRepository(session)
                        use_case = SendTelegramNotificationUseCase(
                            settings_repository=repository,
                            telegram_bot=self._telegram_bot,
                            formatter=self._formatter,
                        )
                        return await use_case.execute_for_agent_action(action)
                
                async def execute_for_vacancy_response(self, response):
                    from domain.use_cases.send_telegram_notification import (
                        SendTelegramNotificationUseCase,
                    )
                    from infrastructure.database.repositories.telegram_notification_settings_repository import (
                        TelegramNotificationSettingsRepository,
                    )
                    
                    async with self._session_factory() as session:
                        repository = TelegramNotificationSettingsRepository(session)
                        use_case = SendTelegramNotificationUseCase(
                            settings_repository=repository,
                            telegram_bot=self._telegram_bot,
                            formatter=self._formatter,
                        )
                        return await use_case.execute_for_vacancy_response(response)
            
            telegram_notification_uc = TelegramNotificationUseCaseWrapper(
                session_factory=session_factory,
                telegram_bot=telegram_bot,
                formatter=formatter,
            )
            
            logger.info("Telegram уведомления включены для EventPublisher")
        except Exception as exc:
            logger.warning(
                f"Не удалось инициализировать Telegram уведомления: {exc}. "
                "Продолжаем без Telegram уведомлений.",
                exc_info=True,
            )
    
    return EventPublisher(get_event_bus(), telegram_notification_use_case=telegram_notification_uc)
