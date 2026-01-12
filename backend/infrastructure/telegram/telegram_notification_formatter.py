"""Форматтер уведомлений для Telegram."""

from __future__ import annotations

from urllib.parse import urlparse

from loguru import logger

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
            elif event_type == "fill_form":
                return self._format_fill_form(action)
            elif event_type == "test_task":
                return self._format_test_task(action)
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
        if response.vacancy_url and self._is_valid_telegram_url(response.vacancy_url):
            keyboard = {
                "inline_keyboard": [[{"text": "Посмотреть вакансию", "url": response.vacancy_url}]],
            }
        elif response.vacancy_url:
            logger.warning(
                f"Пропущено создание кнопки для vacancy_response {response.id}: "
                f"URL {response.vacancy_url} содержит localhost или внутренний IP"
            )

        return text, keyboard

    def _format_call_request(self, action: AgentAction) -> tuple[str, dict | None]:
        """Форматировать запрос на созвон/собеседование."""
        message = action.data.get("message", "")
        text = f"📞 <b>Приглашение на собеседование</b>\n\n"
        text += f"{self._escape_html(message)}"

        chat_url = f"{self._frontend_url}/chats/{action.entity_id}"
        keyboard = None
        if self._is_valid_telegram_url(chat_url):
            keyboard = {
                "inline_keyboard": [[{"text": "Открыть чат", "url": chat_url}]],
            }
        else:
            logger.warning(
                f"Пропущено создание кнопки для call_request action {action.id}: "
                f"URL {chat_url} содержит localhost или внутренний IP"
            )

        return text, keyboard

    def _format_external_action(self, action: AgentAction) -> tuple[str, dict | None]:
        """Форматировать требование действия (анкета, форма)."""
        message = action.data.get("message", "")
        text = f"📋 <b>Требуется заполнить форму</b>\n\n"
        text += f"{self._escape_html(message)}"

        return text, self._build_task_keyboard(action, "Перейти к форме")

    def _format_fill_form(self, action: AgentAction) -> tuple[str, dict | None]:
        """Форматировать запрос на заполнение формы."""
        message = action.data.get("message", "")
        text = f"📝 <b>Заполнить форму</b>\n\n"
        text += f"{self._escape_html(message)}"

        return text, self._build_task_keyboard(action, "Перейти к форме")

    def _format_test_task(self, action: AgentAction) -> tuple[str, dict | None]:
        """Форматировать запрос на тестовое задание."""
        message = action.data.get("message", "")
        text = f"📋 <b>Тестовое задание</b>\n\n"
        text += f"{self._escape_html(message)}"

        return text, self._build_task_keyboard(action, "Перейти к заданию")

    def _format_message_suggestion(self, action: AgentAction) -> tuple[str, dict | None]:
        """Форматировать предложение сообщения для отправки."""
        message_text = action.data.get("message_text", "")
        text = f"💬 <b>Предложено сообщение для отправки</b>\n\n"
        if message_text:
            preview = message_text[:200] + "..." if len(message_text) > 200 else message_text
            text += f"{self._escape_html(preview)}"

        chat_url = f"{self._frontend_url}/chats/{action.entity_id}"
        keyboard = None
        if self._is_valid_telegram_url(chat_url):
            keyboard = {
                "inline_keyboard": [[{"text": "Открыть чат", "url": chat_url}]],
            }
        else:
            logger.warning(
                f"Пропущено создание кнопки для message_suggestion action {action.id}: "
                f"URL {chat_url} содержит localhost или внутренний IP"
            )

        return text, keyboard

    def _format_question_answered(self, action: AgentAction) -> tuple[str, dict | None]:
        """Форматировать ответ на вопрос."""
        message = action.data.get("message", "")
        text = f"💡 <b>Ответ на вопрос</b>\n\n"
        text += f"{self._escape_html(message)}"

        chat_url = f"{self._frontend_url}/chats/{action.entity_id}"
        keyboard = None
        if self._is_valid_telegram_url(chat_url):
            keyboard = {
                "inline_keyboard": [[{"text": "Открыть чат", "url": chat_url}]],
            }
        else:
            logger.warning(
                f"Пропущено создание кнопки для question_answered action {action.id}: "
                f"URL {chat_url} содержит localhost или внутренний IP"
            )

        return text, keyboard

    def _build_task_keyboard(self, action: AgentAction, link_label: str) -> dict | None:
        """Сформировать inline-клавиатуру для заданий."""
        keyboard_rows = []

        link = action.data.get("link")
        if isinstance(link, str) and link:
            if self._is_valid_telegram_url(link):
                keyboard_rows.append([{"text": link_label, "url": link}])
            else:
                logger.warning(
                    f"Пропущено создание кнопки для action {action.id}: "
                    f"URL {link} содержит localhost или внутренний IP"
                )

        chat_url = f"{self._frontend_url}/chats/{action.entity_id}"
        if self._is_valid_telegram_url(chat_url):
            keyboard_rows.append([{"text": "Открыть чат", "url": chat_url}])
        else:
            logger.warning(
                f"Пропущено создание кнопки для action {action.id}: "
                f"URL {chat_url} содержит localhost или внутренний IP"
            )

        if not keyboard_rows:
            return None

        return {"inline_keyboard": keyboard_rows}

    def _format_default_action(self, action: AgentAction) -> tuple[str, dict | None]:
        """Форматировать действие по умолчанию."""
        text = f"🔔 <b>Новое действие агента</b>\n\n"
        text += f"<b>Тип:</b> {self._escape_html(action.type)}"

        return text, None

    def _is_valid_telegram_url(self, url: str) -> bool:
        """Проверить, является ли URL валидным для Telegram.

        Telegram не принимает localhost, 127.0.0.1 и внутренние IP адреса в инлайн кнопках.

        Args:
            url: URL для проверки.

        Returns:
            True если URL валиден для Telegram, False в противном случае.
        """
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname

            if not hostname:
                return False

            # Проверка на localhost
            if hostname.lower() in ("localhost", "127.0.0.1", "::1"):
                return False

            # Проверка на внутренние IP адреса
            parts = hostname.split(".")
            if len(parts) == 4:
                try:
                    octets = [int(part) for part in parts]
                    # 10.0.0.0/8
                    if octets[0] == 10:
                        return False
                    # 172.16.0.0/12
                    if octets[0] == 172 and 16 <= octets[1] <= 31:
                        return False
                    # 192.168.0.0/16
                    if octets[0] == 192 and octets[1] == 168:
                        return False
                except ValueError:
                    pass

            return True
        except Exception as exc:
            logger.warning(f"Ошибка при проверке URL {url}: {exc}")
            return False

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
