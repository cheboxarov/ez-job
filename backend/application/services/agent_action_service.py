"""Сервис приложения для работы с действиями агента."""

from __future__ import annotations

from typing import Any, Dict, List
from uuid import UUID

from domain.entities.agent_action import AgentAction
from domain.interfaces.agent_action_service_port import AgentActionServicePort
from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from domain.use_cases.create_agent_action import CreateAgentActionUseCase
from domain.use_cases.execute_agent_action import ExecuteAgentActionUseCase
from domain.use_cases.list_agent_actions import ListAgentActionsUseCase
from domain.use_cases.send_chat_message import SendChatMessageUseCase
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase
from domain.use_cases.update_agent_action_status import UpdateAgentActionStatusUseCase


class AgentActionService(AgentActionServicePort):
    """Сервис для работы с действиями агента, оркестрирующий use case'ы."""

    def __init__(
        self,
        unit_of_work: UnitOfWorkPort,
        send_chat_message_uc: SendChatMessageUseCase,
    ) -> None:
        """Инициализация сервиса.

        Args:
            unit_of_work: UnitOfWork для управления транзакциями.
            send_chat_message_uc: Use case для отправки сообщений в чат.
        """
        self._unit_of_work = unit_of_work
        self._send_chat_message_uc = send_chat_message_uc

    async def create_action(self, action: AgentAction) -> AgentAction:
        """Создать действие агента в БД.

        Args:
            action: Доменная сущность AgentAction для создания.
                   Поле id может быть не заполнено (будет сгенерировано).

        Returns:
            Созданная доменная сущность AgentAction с заполненными id, created_at и updated_at.

        Raises:
            Exception: При ошибках сохранения в БД.
        """
        async with self._unit_of_work:
            use_case = CreateAgentActionUseCase(
                self._unit_of_work.standalone_agent_action_repository
            )
            result = await use_case.execute(action)
            await self._unit_of_work.commit()
            return result

    async def list_actions(
        self,
        *,
        types: list[str] | None = None,
        exclude_types: list[str] | None = None,
        event_types: list[str] | None = None,
        exclude_event_types: list[str] | None = None,
        statuses: list[str] | None = None,
        entity_type: str | None = None,
        entity_id: int | None = None,
        created_by: str | None = None,
    ) -> List[AgentAction]:
        """Получить список действий агента с опциональной фильтрацией.

        Args:
            types: Фильтр по списку типов действий (например, ["send_message", "create_event"]).
            exclude_types: Исключить указанные типы действий.
            event_types: Фильтр по подтипам событий (data["event_type"]) для create_event.
            exclude_event_types: Исключить указанные подтипы событий (data["event_type"]).
            statuses: Фильтр по статусам (data["status"]) для create_event.
            entity_type: Фильтр по типу сущности (например, "hh_dialog").
            entity_id: Фильтр по ID сущности (например, ID диалога).
            created_by: Фильтр по идентификатору агента (например, "messages_agent").

        Returns:
            Список доменных сущностей AgentAction, отсортированный по created_at (desc).

        Raises:
            Exception: При ошибках получения данных из БД.
        """
        async with self._unit_of_work:
            use_case = ListAgentActionsUseCase(
                self._unit_of_work.standalone_agent_action_repository
            )
            return await use_case.execute(
                types=types,
                exclude_types=exclude_types,
                event_types=event_types,
                exclude_event_types=exclude_event_types,
                statuses=statuses,
                entity_type=entity_type,
                entity_id=entity_id,
                created_by=created_by,
            )

    async def execute_action(
        self,
        action: AgentAction,
        *,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        user_id: UUID | None = None,
    ) -> Dict[str, Any]:
        """Выполнить действие агента.

        Args:
            action: Действие агента для выполнения.
            headers: HTTP заголовки для запросов к HH API.
            cookies: HTTP cookies для запросов к HH API.
            user_id: UUID пользователя для обновления cookies (опционально).

        Returns:
            Результат выполнения действия (зависит от типа действия).

        Raises:
            ValueError: Если тип действия неизвестен или данные действия некорректны.
            Exception: При ошибках выполнения действия.
        """
        # Для выполнения действия не нужна транзакция, так как мы только выполняем действие
        # (отправляем сообщение, создаем событие), но не сохраняем данные в БД
        # Создаем update_cookies_uc, если нужен, используя новый контекст UnitOfWork
        # Контекст должен оставаться открытым во время выполнения действия
        update_cookies_uc = None
        if user_id:
            # Создаем update_cookies_uc внутри контекста
            # Контекст будет закрыт после выполнения действия
            async with self._unit_of_work:
                update_cookies_uc = UpdateUserHhAuthCookiesUseCase(
                    self._unit_of_work.standalone_user_hh_auth_data_repository
                )

                use_case = ExecuteAgentActionUseCase(
                    agent_action_repository=self._unit_of_work.standalone_agent_action_repository,
                    send_chat_message_uc=self._send_chat_message_uc,
                )

                return await use_case.execute(
                    action=action,
                    headers=headers,
                    cookies=cookies,
                    user_id=user_id,
                    update_cookies_uc=update_cookies_uc,
                )

        # Если user_id не передан, выполняем без обновления cookies
        use_case = ExecuteAgentActionUseCase(
            agent_action_repository=self._unit_of_work.standalone_agent_action_repository,
            send_chat_message_uc=self._send_chat_message_uc,
        )

        return await use_case.execute(
            action=action,
            headers=headers,
            cookies=cookies,
            user_id=user_id,
            update_cookies_uc=None,
        )

    async def create_and_execute_action(
        self,
        action: AgentAction,
        *,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        user_id: UUID | None = None,
    ) -> tuple[AgentAction, Dict[str, Any]]:
        """Создать действие агента в БД и выполнить его.

        Args:
            action: Действие агента для создания и выполнения.
            headers: HTTP заголовки для запросов к HH API.
            cookies: HTTP cookies для запросов к HH API.
            user_id: UUID пользователя для обновления cookies (опционально).

        Returns:
            Кортеж из созданной доменной сущности AgentAction и результата выполнения.

        Raises:
            ValueError: Если тип действия неизвестен или данные действия некорректны.
            Exception: При ошибках создания или выполнения действия.
        """
        # Сначала создаем действие в БД
        created_action = await self.create_action(action)

        # Затем выполняем действие
        # Используем тот же подход, что и в execute_action
        if user_id:
            async with self._unit_of_work:
                update_cookies_uc = UpdateUserHhAuthCookiesUseCase(
                    self._unit_of_work.standalone_user_hh_auth_data_repository
                )

                use_case = ExecuteAgentActionUseCase(
                    agent_action_repository=self._unit_of_work.standalone_agent_action_repository,
                    send_chat_message_uc=self._send_chat_message_uc,
                )

                result = await use_case.execute(
                    action=created_action,
                    headers=headers,
                    cookies=cookies,
                    user_id=user_id,
                    update_cookies_uc=update_cookies_uc,
                )

                return created_action, result

        # Если user_id не передан, выполняем без обновления cookies
        use_case = ExecuteAgentActionUseCase(
            agent_action_repository=self._unit_of_work.standalone_agent_action_repository,
            send_chat_message_uc=self._send_chat_message_uc,
        )

        result = await use_case.execute(
            action=created_action,
            headers=headers,
            cookies=cookies,
            user_id=user_id,
            update_cookies_uc=None,
        )

        return created_action, result

    async def get_unread_count(self, user_id: UUID) -> int:
        async with self._unit_of_work:
            return await self._unit_of_work.standalone_agent_action_repository.get_unread_count(
                user_id
            )

    async def mark_all_as_read(self, user_id: UUID) -> None:
        async with self._unit_of_work:
            await self._unit_of_work.standalone_agent_action_repository.mark_all_as_read(user_id)
            await self._unit_of_work.commit()

    async def update_action_status(
        self,
        *,
        action_id: UUID,
        status: str,
        user_id: UUID,
    ) -> AgentAction:
        """Обновить статус события (fill_form/test_task)."""
        async with self._unit_of_work:
            use_case = UpdateAgentActionStatusUseCase(
                self._unit_of_work.standalone_agent_action_repository
            )
            updated_action = await use_case.execute(
                action_id=action_id,
                status=status,
                user_id=user_id,
            )
            await self._unit_of_work.commit()
            return updated_action
