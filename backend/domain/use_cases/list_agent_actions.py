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
        try:
            logger.info(
                "Получение списка действий агента: "
                f"types={types}, exclude_types={exclude_types}, "
                f"event_types={event_types}, exclude_event_types={exclude_event_types}, "
                f"statuses={statuses}, "
                f"entity_type={entity_type}, entity_id={entity_id}, created_by={created_by}"
            )
            actions = await self._agent_action_repository.list(
                types=types,
                exclude_types=exclude_types,
                event_types=event_types,
                exclude_event_types=exclude_event_types,
                statuses=statuses,
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
