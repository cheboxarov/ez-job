"""Интерфейс репозитория действий агента."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

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
        type: str | None = None,
        entity_type: str | None = None,
        entity_id: int | None = None,
        created_by: str | None = None,
    ) -> List[AgentAction]:
        """Получить список действий с опциональной фильтрацией.

        Все переданные параметры (не None) объединяются через AND.
        Если все параметры None, возвращаются все действия.

        Args:
            type: Фильтр по типу действия (например, "send_message", "create_event").
            entity_type: Фильтр по типу сущности (например, "hh_dialog").
            entity_id: Фильтр по ID сущности (например, ID диалога).
            created_by: Фильтр по идентификатору агента (например, "messages_agent").

        Returns:
            Список доменных сущностей AgentAction, отсортированный по created_at (desc).
        """

