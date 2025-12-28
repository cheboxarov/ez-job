"""Воркер для Telegram бота."""

from __future__ import annotations

import asyncio
import signal
import sys
from pathlib import Path

from loguru import logger

# Добавляем корневую директорию проекта в путь
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from config import AppConfig, load_config
from infrastructure.database.session import create_session_factory
from infrastructure.telegram.telegram_bot import TelegramBot
from domain.use_cases.link_telegram_account import LinkTelegramAccountUseCase
from domain.use_cases.unlink_telegram_account import UnlinkTelegramAccountUseCase
from infrastructure.database.repositories.telegram_notification_settings_repository import (
    TelegramNotificationSettingsRepository,
)
from infrastructure.database.repositories.telegram_link_token_repository import (
    TelegramLinkTokenRepository,
)

# Настройка loguru
logger.add(
    "logs/telegram_bot_worker_{time}.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    enqueue=True,  # Для асинхронной записи
)

# Флаг для корректного завершения (используется только при запуске как отдельного процесса)
shutdown_event = asyncio.Event()


def setup_signal_handlers(loop: asyncio.AbstractEventLoop, shutdown_event: asyncio.Event) -> None:
    """Настройка обработчиков сигналов для корректного завершения."""
    def signal_handler(signum: int) -> None:
        """Обработчик сигналов для корректного завершения."""
        logger.info(f"Получен сигнал {signum}, завершаем работу...")
        shutdown_event.set()
    
    # Используем add_signal_handler для правильной работы с asyncio
    if sys.platform != "win32":
        loop.add_signal_handler(signal.SIGINT, signal_handler, signal.SIGINT)
        loop.add_signal_handler(signal.SIGTERM, signal_handler, signal.SIGTERM)
    else:
        # На Windows используем signal.signal
        signal.signal(signal.SIGINT, lambda s, f: signal_handler(s))
        signal.signal(signal.SIGTERM, lambda s, f: signal_handler(s))


async def run_worker(config: AppConfig, shutdown_event: asyncio.Event | None = None) -> None:
    """Запустить воркер для Telegram бота.
    
    Args:
        config: Конфигурация приложения.
        shutdown_event: Событие для управления остановкой воркера. Если None, используется глобальное.
    """
    if shutdown_event is None:
        shutdown_event = globals()["shutdown_event"]
    
    if not config.telegram.bot_token:
        logger.warning("Telegram bot_token не настроен, воркер не будет запущен")
        return
    
    logger.info("Запуск воркера Telegram бота")
    
    session_factory = create_session_factory(config.database)
    
    # Создаем handlers для привязки/отвязки
    async def link_handler(chat_id: int, token: str | None, username: str | None = None) -> None:
        """Обработчик привязки Telegram аккаунта."""
        if not token:
            raise ValueError("Токен не предоставлен")
        
        async with session_factory() as session:
            link_uc = LinkTelegramAccountUseCase(
                token_repository=TelegramLinkTokenRepository(session),
                settings_repository=TelegramNotificationSettingsRepository(session),
            )
            await link_uc.execute(
                telegram_chat_id=chat_id,
                telegram_username=username,
                token=token,
            )
            await session.commit()
    
    async def unlink_handler(chat_id: int) -> None:
        """Обработчик отвязки Telegram аккаунта."""
        async with session_factory() as session:
            settings_repo = TelegramNotificationSettingsRepository(session)
            settings = await settings_repo.get_by_telegram_chat_id(chat_id)
            if settings:
                unlink_uc = UnlinkTelegramAccountUseCase(
                    settings_repository=settings_repo,
                )
                await unlink_uc.execute(settings.user_id)
                await session.commit()
    
    # Создаем и запускаем бота
    telegram_bot = TelegramBot(
        bot_token=config.telegram.bot_token,
        link_token_handler=link_handler,
        unlink_handler=unlink_handler,
    )
    
    try:
        # Запускаем бота
        await telegram_bot.start_polling()
        logger.info("Telegram бот запущен")
        
        # Ждем сигнала остановки
        await shutdown_event.wait()
        logger.info("Получен сигнал остановки, завершаем работу бота...")
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания (Ctrl+C)")
    except Exception as exc:
        logger.error(f"Критическая ошибка в воркере Telegram бота: {exc}", exc_info=True)
        raise
    finally:
        # Останавливаем бота
        try:
            await telegram_bot.stop()
            logger.info("Telegram бот остановлен")
        except Exception as exc:
            logger.error(f"Ошибка при остановке Telegram бота: {exc}", exc_info=True)


async def main() -> None:
    """Главная функция воркера (используется при запуске как отдельного процесса)."""
    # Получаем текущий event loop
    loop = asyncio.get_running_loop()
    
    # Регистрируем обработчики сигналов
    setup_signal_handlers(loop, shutdown_event)
    
    # Загружаем конфигурацию
    config = load_config()
    
    try:
        await run_worker(config, shutdown_event)
    except Exception as exc:
        logger.error(f"Критическая ошибка: {exc}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
