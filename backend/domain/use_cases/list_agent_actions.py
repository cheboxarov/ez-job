"""Use case для получения списка действий агента."""

from __future__ import annotations

from typing import List

from loguru import logger

from domain.entities.agent_action import AgentAction
from domain.interfaces.agent_action_repository_port import AgentActionRepositoryPort


class ListAgentActionsUseCase:
    """Use case для получения списка действий агента с опциональной фильтрацией."""

    def __init__(self, agent_action_repository: AgentActionRepositoryPort) -> None:
        """Инициализация use case.

        Args:
            agent_action_repository: Репозиторий для работы с действиями агента.
        """
        self._agent_action_repository = agent_action_repository

    async def execute(
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
        try:
            logger.info(
                f"Получение списка действий агента: type={type}, "
                f"entity_type={entity_type}, entity_id={entity_id}, created_by={created_by}"
            )
            actions = await self._agent_action_repository.list(
                type=type,
                entity_type=entity_type,
                entity_id=entity_id,
                created_by=created_by,
            )
            logger.info(f"Получено {len(actions)} действий агента")
            return actions
        except Exception as exc:
            logger.error(
                f"Ошибка при получении списка действий агента: {exc}",
                exc_info=True,
            )
            raise

