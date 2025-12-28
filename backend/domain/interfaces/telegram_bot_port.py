"""Интерфейс для Telegram бота."""

from __future__ import annotations

from abc import ABC, abstractmethod


class TelegramBotPort(ABC):
    """Порт для Telegram бота.

    Инфраструктура должна реализовать этот интерфейс.
    """

    @abstractmethod
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
