"""Use case для пометки AgentAction как отправленного."""

from __future__ import annotations

from datetime import datetime, timezone

from loguru import logger

from domain.entities.agent_action import AgentAction
from domain.interfaces.agent_action_repository_port import AgentActionRepositoryPort


class MarkAgentActionAsSentUseCase:
    """Use case для пометки AgentAction как отправленного.

    Обновляет поле data["sended"] = True в AgentAction.
    """

    def __init__(self, agent_action_repository: AgentActionRepositoryPort) -> None:
        """Инициализация use case.

        Args:
            agent_action_repository: Репозиторий для работы с действиями агента.
        """
        self._agent_action_repository = agent_action_repository

    async def execute(self, action: AgentAction) -> AgentAction:
        """Пометить AgentAction как отправленный.

        Args:
            action: Действие агента для пометки.

        Returns:
            Обновленная доменная сущность AgentAction с data["sended"] = True.

        Raises:
            Exception: При ошибках работы с БД.
        """
        try:
            # Обновляем поле sended в data
            action.data["sended"] = True
            action.updated_at = datetime.now(timezone.utc)

            # Сохраняем изменения через репозиторий
            updated_action = await self._agent_action_repository.update(action)

            logger.info(f"AgentAction {action.id} помечен как отправленный")

            return updated_action
        except Exception as exc:
            logger.error(
                f"Ошибка при пометке AgentAction {action.id} как отправленного: {exc}",
                exc_info=True,
            )
            raise
