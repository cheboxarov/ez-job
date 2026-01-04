"""Telegram бот для уведомлений."""

from __future__ import annotations

import asyncio
from typing import Callable

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

from domain.interfaces.telegram_bot_port import TelegramBotPort


class TelegramBot(TelegramBotPort):
    """Реализация Telegram бота."""

    def __init__(
        self,
        bot_token: str,
        link_token_handler: Callable[[int, str | None, str | None], None] | None = None,
        unlink_handler: Callable[[int], None] | None = None,
    ) -> None:
        """Инициализация бота.

        Args:
            bot_token: Токен бота от @BotFather.
            link_token_handler: Обработчик для команды /start TOKEN (chat_id, token).
            unlink_handler: Обработчик для команды /unlink (chat_id).
        """
        self._bot = Bot(token=bot_token)
        self._dp = Dispatcher()
        self._router = Router()
        self._link_token_handler = link_token_handler
        self._unlink_handler = unlink_handler
        self._polling_task: asyncio.Task | None = None
        self._shutdown_event = asyncio.Event()
        self._setup_handlers()
        self._dp.include_router(self._router)

    def _setup_handlers(self) -> None:
        """Настройка обработчиков команд."""

        @self._router.message(Command("start"))
        async def handle_start(message: Message) -> None:
            """Обработка команды /start или /start TOKEN."""
            chat_id = message.chat.id
            username = message.from_user.username if message.from_user else None

            if message.text and len(message.text.split()) > 1:
                token = message.text.split()[1]
                logger.info(f"Получен запрос на привязку: chat_id={chat_id}, token={token}, username={username}")
                if self._link_token_handler:
                    try:
                        await self._link_token_handler(chat_id, token, username)
                        await message.answer(
                            "✅ Telegram успешно привязан!\n\n"
                            "Теперь вы будете получать уведомления о важных событиях."
                        )
                    except Exception as exc:
                        logger.error(f"Ошибка при привязке: {exc}", exc_info=True)
                        await message.answer(
                            "❌ Ошибка при привязке аккаунта. "
                            "Токен недействителен или истёк. Попробуйте создать новую ссылку."
                        )
            else:
                help_text = (
                    "👋 Привет! Это бот для уведомлений о событиях в приложении.\n\n"
                    "Чтобы привязать аккаунт, используйте ссылку из настроек приложения."
                )
                await message.answer(help_text)

        @self._router.message(Command("unlink"))
        async def handle_unlink(message: Message) -> None:
            """Обработка команды /unlink."""
            chat_id = message.chat.id
            logger.info(f"Получен запрос на отвязку: chat_id={chat_id}")
            if self._unlink_handler:
                try:
                    await self._unlink_handler(chat_id)
                    await message.answer("✅ Telegram успешно отвязан. Уведомления больше не будут приходить.")
                except Exception as exc:
                    logger.error(f"Ошибка при отвязке: {exc}", exc_info=True)
                    await message.answer("❌ Ошибка при отвязке аккаунта.")
            else:
                await message.answer("❌ Команда отвязки недоступна.")

        @self._router.message(Command("help"))
        async def handle_help(message: Message) -> None:
            """Обработка команды /help."""
            help_text = (
                "📖 Доступные команды:\n\n"
                "/start [TOKEN] - Привязать аккаунт (используйте ссылку из приложения)\n"
                "/unlink - Отвязать аккаунт\n"
                "/help - Показать эту справку\n\n"
                "Для настройки уведомлений используйте веб-приложение."
            )
            await message.answer(help_text)

    async def start_polling(self) -> None:
        """Запустить polling."""
        if self._polling_task and not self._polling_task.done():
            logger.warning("Bot уже запущен")
            return

        logger.info("Запуск Telegram бота в режиме polling...")
        self._shutdown_event.clear()

        async def polling_loop() -> None:
            try:
                await self._dp.start_polling(self._bot)
            except Exception as exc:
                logger.error(f"Ошибка в polling: {exc}", exc_info=True)
                raise

        self._polling_task = asyncio.create_task(polling_loop())
        logger.info("Telegram бот запущен")

    async def stop(self) -> None:
        """Остановить бота."""
        logger.info("Остановка Telegram бота...")
        self._shutdown_event.set()

        if self._polling_task and not self._polling_task.done():
            await self._dp.stop_polling()
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass

        await self._bot.session.close()
        logger.info("Telegram бот остановлен")

    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str = "HTML",
        reply_markup: dict | None = None,
    ) -> bool:
        """Отправить сообщение в Telegram.

        Args:
            chat_id: ID чата в Telegram.
            text: Текст сообщения.
            parse_mode: Режим парсинга (HTML, Markdown).
            reply_markup: Inline клавиатура (опционально).

        Returns:
            True если сообщение отправлено успешно, False в противном случае.
        """
        try:
            from aiogram.types import InlineKeyboardMarkup

            markup = None
            if reply_markup:
                markup = InlineKeyboardMarkup.model_validate(reply_markup)

            await self._bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=markup,
            )
            return True
        except Exception as exc:
            logger.error(f"Ошибка при отправке сообщения в Telegram: {exc}", exc_info=True)
            
            # Если была клавиатура и произошла ошибка, пробуем отправить без неё
            if reply_markup:
                logger.warning(
                    f"Попытка ретрая отправки сообщения без клавиатуры для chat_id={chat_id}. "
                    f"Ошибка: {exc}"
                )
                try:
                    await self._bot.send_message(
                        chat_id=chat_id,
                        text=text,
                        parse_mode=parse_mode,
                        reply_markup=None,
                    )
                    logger.info(f"Сообщение успешно отправлено без клавиатуры для chat_id={chat_id}")
                    return True
                except Exception as retry_exc:
                    logger.error(
                        f"Ошибка при ретрае отправки сообщения без клавиатуры: {retry_exc}",
                        exc_info=True,
                    )
                    return False
            
            return False
