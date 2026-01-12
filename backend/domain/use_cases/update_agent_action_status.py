"""Use case для обновления статуса события AgentAction."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from loguru import logger

from domain.entities.agent_action import AgentAction
from domain.interfaces.agent_action_repository_port import AgentActionRepositoryPort


class UpdateAgentActionStatusUseCase:
    """Use case для обновления статуса событий типа fill_form/test_task."""

    _ALLOWED_EVENT_TYPES = {"fill_form", "test_task"}
    _ALLOWED_STATUSES = {"pending", "completed", "declined"}

    def __init__(self, agent_action_repository: AgentActionRepositoryPort) -> None:
        """Инициализация use case.

        Args:
            agent_action_repository: Репозиторий для работы с действиями агента.
        """
        self._agent_action_repository = agent_action_repository

    async def execute(
        self,
        *,
        action_id: UUID,
        status: str,
        user_id: UUID,
    ) -> AgentAction:
        """Обновить статус события.

        Args:
            action_id: UUID действия агента.
            status: Новый статус ("pending", "completed", "declined").
            user_id: UUID пользователя для проверки прав доступа.

        Returns:
            Обновленная доменная сущность AgentAction.

        Raises:
            ValueError: Если действие не найдено, не принадлежит пользователю,
                        не является fill_form/test_task или статус некорректен.
        """
        action = await self._agent_action_repository.get_by_id(action_id)

        if action is None:
            raise ValueError(f"Действие с ID {action_id} не найдено")

        if action.user_id != user_id:
            raise ValueError(f"Действие {action_id} не принадлежит пользователю {user_id}")

        if action.type != "create_event":
            raise ValueError(f"Действие {action_id} не является типом create_event")

        event_type = action.data.get("event_type")
        if event_type not in self._ALLOWED_EVENT_TYPES:
            raise ValueError(
                f"Действие {action_id} не поддерживает обновление статуса (event_type: {event_type})"
            )

        if status not in self._ALLOWED_STATUSES:
            raise ValueError(f"Некорректный статус: {status}")

        action.data["status"] = status
        action.updated_at = datetime.now(timezone.utc)

        updated_action = await self._agent_action_repository.update(action)
        logger.info(f"Статус действия {action_id} обновлен на {status}")
        return updated_action
