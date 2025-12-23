"""Use case для создания действия агента в БД."""

from __future__ import annotations

from loguru import logger

from domain.entities.agent_action import AgentAction
from domain.interfaces.agent_action_repository_port import AgentActionRepositoryPort


class CreateAgentActionUseCase:
    """Use case для создания действия агента в БД.

    Базовый use case для сохранения действия агента в базе данных.
    """

    def __init__(self, agent_action_repository: AgentActionRepositoryPort) -> None:
        """Инициализация use case.

        Args:
            agent_action_repository: Репозиторий для работы с действиями агента.
        """
        self._agent_action_repository = agent_action_repository

    async def execute(self, action: AgentAction) -> AgentAction:
        """Создать действие агента в БД.

        Args:
            action: Доменная сущность AgentAction для создания.
                   Поле id может быть не заполнено (будет сгенерировано).

        Returns:
            Созданная доменная сущность AgentAction с заполненными id, created_at и updated_at.

        Raises:
            Exception: При ошибках сохранения в БД.
        """
        try:
            logger.info(
                f"Создание действия агента: type={action.type}, "
                f"entity_type={action.entity_type}, entity_id={action.entity_id}, "
                f"created_by={action.created_by}"
            )
            result = await self._agent_action_repository.create(action)
            logger.info(
                f"Успешно создано действие агента: id={result.id}, type={result.type}, "
                f"entity_type={result.entity_type}, entity_id={result.entity_id}"
            )
            return result
        except Exception as exc:
            logger.error(
                f"Ошибка при создании действия агента type={action.type}, "
                f"entity_type={action.entity_type}, entity_id={action.entity_id}: {exc}",
                exc_info=True,
            )
            raise

