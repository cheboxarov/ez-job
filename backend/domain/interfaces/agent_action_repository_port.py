"""Интерфейс репозитория действий агента."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from domain.entities.agent_action import AgentAction


class AgentActionRepositoryPort(ABC):
    """Порт репозитория действий агента.

    Инфраструктура должна реализовать этот интерфейс.
    """

    @abstractmethod
    async def create(self, action: AgentAction) -> AgentAction:
        """Создать действие агента.

        Args:
            action: Доменная сущность AgentAction для создания.
                   Поле id может быть не заполнено (будет сгенерировано).

        Returns:
            Созданная доменная сущность AgentAction с заполненными id, created_at и updated_at.
        """

    @abstractmethod
    async def list(
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
        """Получить список действий с опциональной фильтрацией.

        Все переданные параметры (не None) объединяются через AND.
        Если все параметры None, возвращаются все действия.

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
        """
    @abstractmethod
    async def get_unread_count(self, user_id: UUID) -> int:
        """Получить количество непрочитанных действий для пользователя."""

    @abstractmethod
    async def mark_all_as_read(self, user_id: UUID) -> None:
        """Пометить все действия пользователя как прочитанные."""

    @abstractmethod
    async def update(self, action: AgentAction) -> AgentAction:
        """Обновить действие агента.

        Args:
            action: Доменная сущность AgentAction с обновленными данными.

        Returns:
            Обновленная доменная сущность AgentAction.

        Raises:
            ValueError: Если действие с таким ID не найдено.
        """

    @abstractmethod
    async def get_by_id(self, action_id: UUID) -> AgentAction | None:
        """Получить действие агента по ID.

        Args:
            action_id: UUID действия.

        Returns:
            Доменная сущность AgentAction или None, если не найдено.
        """
