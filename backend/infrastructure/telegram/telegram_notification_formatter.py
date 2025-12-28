"""Форматтер уведомлений для Telegram."""

from __future__ import annotations

from domain.entities.agent_action import AgentAction
from domain.entities.vacancy_response import VacancyResponse


class TelegramNotificationFormatter:
    """Форматтер для форматирования уведомлений в Telegram."""

    def __init__(self, frontend_url: str) -> None:
        """Инициализация форматтера.

        Args:
            frontend_url: URL фронтенда для формирования ссылок.
        """
        self._frontend_url = frontend_url.rstrip("/")

    def format_agent_action(self, action: AgentAction) -> tuple[str, dict | None]:
        """Форматировать AgentAction для отправки в Telegram.

        Args:
            action: Действие агента.

        Returns:
            Кортеж (текст сообщения, inline клавиатура или None).
        """
        if action.type == "send_message":
            return self._format_message_suggestion(action)
        elif action.type == "create_event":
            event_type = action.data.get("event_type")
            if event_type == "call_request":
                return self._format_call_request(action)
            elif event_type == "external_action_request":
                return self._format_external_action(action)
            elif event_type == "question_answered":
                return self._format_question_answered(action)

        return self._format_default_action(action)

    def format_vacancy_response(self, response: VacancyResponse) -> tuple[str, dict | None]:
        """Форматировать VacancyResponse для отправки в Telegram.

        Args:
            response: Отклик на вакансию.

        Returns:
            Кортеж (текст сообщения, inline клавиатура или None).
        """
        text = f"✅ <b>Отклик отправлен</b>\n\n"
        text += f"<b>Вакансия:</b> {self._escape_html(response.vacancy_name)}\n"

        keyboard = None
        if response.vacancy_url:
            keyboard = {
                "inline_keyboard": [[{"text": "Посмотреть вакансию", "url": response.vacancy_url}]],
            }

        return text, keyboard

    def _format_call_request(self, action: AgentAction) -> tuple[str, dict | None]:
        """Форматировать запрос на созвон/собеседование."""
        message = action.data.get("message", "")
        text = f"📞 <b>Приглашение на собеседование</b>\n\n"
        text += f"{self._escape_html(message)}"

        chat_url = f"{self._frontend_url}/chats/{action.entity_id}"
        keyboard = {
            "inline_keyboard": [[{"text": "Открыть чат", "url": chat_url}]],
        }

        return text, keyboard

    def _format_external_action(self, action: AgentAction) -> tuple[str, dict | None]:
        """Форматировать требование действия (анкета, форма)."""
        message = action.data.get("message", "")
        text = f"📋 <b>Требуется заполнить форму</b>\n\n"
        text += f"{self._escape_html(message)}"

        chat_url = f"{self._frontend_url}/chats/{action.entity_id}"
        keyboard = {
            "inline_keyboard": [[{"text": "Открыть чат", "url": chat_url}]],
        }

        return text, keyboard

    def _format_message_suggestion(self, action: AgentAction) -> tuple[str, dict | None]:
        """Форматировать предложение сообщения для отправки."""
        message_text = action.data.get("message_text", "")
        text = f"💬 <b>Предложено сообщение для отправки</b>\n\n"
        if message_text:
            preview = message_text[:200] + "..." if len(message_text) > 200 else message_text
            text += f"{self._escape_html(preview)}"

        chat_url = f"{self._frontend_url}/chats/{action.entity_id}"
        keyboard = {
            "inline_keyboard": [[{"text": "Открыть чат", "url": chat_url}]],
        }

        return text, keyboard

    def _format_question_answered(self, action: AgentAction) -> tuple[str, dict | None]:
        """Форматировать ответ на вопрос."""
        message = action.data.get("message", "")
        text = f"💡 <b>Ответ на вопрос</b>\n\n"
        text += f"{self._escape_html(message)}"

        chat_url = f"{self._frontend_url}/chats/{action.entity_id}"
        keyboard = {
            "inline_keyboard": [[{"text": "Открыть чат", "url": chat_url}]],
        }

        return text, keyboard

    def _format_default_action(self, action: AgentAction) -> tuple[str, dict | None]:
        """Форматировать действие по умолчанию."""
        text = f"🔔 <b>Новое действие агента</b>\n\n"
        text += f"<b>Тип:</b> {self._escape_html(action.type)}"

        return text, None

    def _escape_html(self, text: str) -> str:
        """Экранировать HTML символы.

        Args:
            text: Текст для экранирования.

        Returns:
            Экранированный текст.
        """
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
