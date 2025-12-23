"""Use case для выполнения действия агента."""

from __future__ import annotations

from typing import Any, Dict
from uuid import UUID

from loguru import logger

from domain.entities.agent_action import AgentAction
from domain.interfaces.agent_action_repository_port import AgentActionRepositoryPort
from domain.use_cases.send_chat_message import SendChatMessageUseCase
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase


class ExecuteAgentActionUseCase:
    """Use case для выполнения действия агента.

    Выполняет действие агента в зависимости от его типа:
    - "send_message": отправляет сообщение в чат через SendChatMessageUseCase
    - "create_event": логирует событие (требует дополнительной обработки)
    """

    def __init__(
        self,
        agent_action_repository: AgentActionRepositoryPort,
        send_chat_message_uc: SendChatMessageUseCase,
    ) -> None:
        """Инициализация use case.

        Args:
            agent_action_repository: Репозиторий для работы с действиями агента.
            send_chat_message_uc: Use case для отправки сообщений в чат.
        """
        self._agent_action_repository = agent_action_repository
        self._send_chat_message_uc = send_chat_message_uc

    async def execute(
        self,
        action: AgentAction,
        *,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        user_id: UUID | None = None,
        update_cookies_uc: UpdateUserHhAuthCookiesUseCase | None = None,
    ) -> Dict[str, Any]:
        """Выполнить действие агента.

        Args:
            action: Действие агента для выполнения.
            headers: HTTP заголовки для запросов к HH API.
            cookies: HTTP cookies для запросов к HH API.
            user_id: UUID пользователя для обновления cookies (опционально).
            update_cookies_uc: Use case для обновления cookies (опционально).

        Returns:
            Результат выполнения действия (зависит от типа действия).

        Raises:
            ValueError: Если тип действия неизвестен или данные действия некорректны.
            Exception: При ошибках выполнения действия.
        """
        try:
            logger.info(
                f"Выполнение действия агента: id={action.id}, type={action.type}, "
                f"entity_type={action.entity_type}, entity_id={action.entity_id}"
            )

            if action.type == "send_message":
                return await self._execute_send_message(
                    action=action,
                    headers=headers,
                    cookies=cookies,
                    user_id=user_id,
                    update_cookies_uc=update_cookies_uc,
                )
            elif action.type == "create_event":
                return await self._execute_create_event(action)
            else:
                error_msg = f"Неизвестный тип действия: {action.type}"
                logger.error(error_msg)
                raise ValueError(error_msg)

        except Exception as exc:
            logger.error(
                f"Ошибка при выполнении действия агента id={action.id}, type={action.type}: {exc}",
                exc_info=True,
            )
            raise

    async def _execute_send_message(
        self,
        action: AgentAction,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        user_id: UUID | None,
        update_cookies_uc: UpdateUserHhAuthCookiesUseCase | None,
    ) -> Dict[str, Any]:
        """Выполнить отправку сообщения.

        Args:
            action: Действие типа "send_message".
            headers: HTTP заголовки для запросов к HH API.
            cookies: HTTP cookies для запросов к HH API.
            user_id: UUID пользователя для обновления cookies.
            update_cookies_uc: Use case для обновления cookies.

        Returns:
            Результат отправки сообщения от HH API.

        Raises:
            ValueError: Если данные действия некорректны.
        """
        data = action.data
        dialog_id = data.get("dialog_id")
        message_text = data.get("message_text")
        message_to = data.get("message_to")

        if not isinstance(dialog_id, int):
            raise ValueError(f"dialog_id должен быть int, получен: {type(dialog_id)}")
        if not isinstance(message_text, str) or not message_text.strip():
            raise ValueError("message_text должен быть непустой строкой")

        logger.info(
            f"Отправка сообщения: dialog_id={dialog_id}, message_to={message_to}, "
            f"message_text_length={len(message_text)}"
        )

        result = await self._send_chat_message_uc.execute(
            chat_id=dialog_id,
            text=message_text,
            headers=headers,
            cookies=cookies,
            user_id=user_id,
            update_cookies_uc=update_cookies_uc,
        )

        logger.info(f"Сообщение успешно отправлено в диалог {dialog_id}")
        return result

    async def _execute_create_event(self, action: AgentAction) -> Dict[str, Any]:
        """Выполнить создание события.

        Args:
            action: Действие типа "create_event".

        Returns:
            Результат создания события (пока только логирование).

        Raises:
            ValueError: Если данные действия некорректны.
        """
        data = action.data
        dialog_id = data.get("dialog_id")
        event_type = data.get("event_type")
        message = data.get("message")

        if not isinstance(dialog_id, int):
            raise ValueError(f"dialog_id должен быть int, получен: {type(dialog_id)}")
        if not isinstance(event_type, str) or not event_type.strip():
            raise ValueError("event_type должен быть непустой строкой")
        if not isinstance(message, str) or not message.strip():
            raise ValueError("message должен быть непустой строкой")

        logger.info(
            f"Создание события: dialog_id={dialog_id}, event_type={event_type}, "
            f"message={message[:100]}..."
        )

        # TODO: Реализовать обработку событий (уведомления, сохранение в БД и т.д.)
        # Пока только логируем
        return {
            "success": True,
            "dialog_id": dialog_id,
            "event_type": event_type,
            "message": message,
        }

