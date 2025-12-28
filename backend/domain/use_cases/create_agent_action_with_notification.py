"""Use case для создания действия агента с уведомлением через WebSocket."""

from __future__ import annotations

from loguru import logger

from domain.entities.agent_action import AgentAction
from domain.interfaces.event_publisher_port import EventPublisherPort
from domain.use_cases.create_agent_action import CreateAgentActionUseCase


class CreateAgentActionWithNotificationUseCase:
    """Use case для создания AgentAction с уведомлением через WebSocket.
    
    Создаёт действие агента и публикует событие в Event Bus для отправки через WebSocket.
    """

    def __init__(
        self,
        create_agent_action_uc: CreateAgentActionUseCase,
        event_publisher: EventPublisherPort,
    ) -> None:
        """Инициализация use case.
        
        Args:
            create_agent_action_uc: Use case для создания действия агента.
            event_publisher: Publisher для публикации событий.
        """
        self._create_agent_action_uc = create_agent_action_uc
        self._event_publisher = event_publisher

    async def execute(self, action: AgentAction) -> AgentAction:
        """Создать действие агента и опубликовать событие.
        
        Args:
            action: Доменная сущность AgentAction для создания.
                   Поле id может быть не заполнено (будет сгенерировано).
        
        Returns:
            Созданная доменная сущность AgentAction с заполненными id, created_at и updated_at.
        
        Raises:
            Exception: При ошибках сохранения в БД или публикации события.
        """
        try:
            # 1. Создаём action через оригинальный use case
            created_action = await self._create_agent_action_uc.execute(action)
            
            # 2. Публикуем событие (не блокируем создание, если публикация не удалась)
            try:
                await self._event_publisher.publish_agent_action_created(created_action)
                logger.debug(
                    f"Событие agent_action_created опубликовано для действия {created_action.id}"
                )
            except Exception as exc:
                logger.error(
                    f"Ошибка при публикации события agent_action_created для действия {created_action.id}: {exc}",
                    exc_info=True,
                )
                # Не прерываем выполнение, если публикация не удалась
            
            return created_action
        except Exception as exc:
            logger.error(
                f"Ошибка при создании действия агента с уведомлением: {exc}",
                exc_info=True,
            )
            raise
