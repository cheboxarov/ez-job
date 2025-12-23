"""Интерфейс сервиса для работы с действиями агента."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from uuid import UUID

from domain.entities.agent_action import AgentAction


class AgentActionServicePort(ABC):
    """Порт сервиса для работы с действиями агента.

    Application слой должен реализовать этот интерфейс.
    Сервис оркестрирует use case'ы для работы с действиями агента.
    """

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
    async def list_actions(
        self,
        *,
        type: str | None = None,
        entity_type: str | None = None,
        entity_id: int | None = None,
        created_by: str | None = None,
    ) -> List[AgentAction]:
        """Получить список действий агента с опциональной фильтрацией.

        Args:
            type: Фильтр по типу действия (например, "send_message", "create_event").
            entity_type: Фильтр по типу сущности (например, "hh_dialog").
            entity_id: Фильтр по ID сущности (например, ID диалога).
            created_by: Фильтр по идентификатору агента (например, "messages_agent").

        Returns:
            Список доменных сущностей AgentAction, отсортированный по created_at (desc).

        Raises:
            Exception: При ошибках получения данных из БД.
        """
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
    async def create_and_execute_action(
        self,
        action: AgentAction,
        *,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        user_id: UUID | None = None,
    ) -> tuple[AgentAction, Dict[str, Any]]:
        """Создать действие агента в БД и выполнить его."""
        raise NotImplementedError

    @abstractmethod
    async def get_unread_count(self, user_id: UUID) -> int:
        """Получить количество непрочитанных действий для пользователя."""
        raise NotImplementedError

    @abstractmethod
    async def mark_all_as_read(self, user_id: UUID) -> None:
        """Пометить все действия пользователя как прочитанные."""
        raise NotImplementedError

