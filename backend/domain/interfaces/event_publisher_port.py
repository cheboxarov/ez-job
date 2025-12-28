"""Интерфейс для публикации событий."""

from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities.agent_action import AgentAction
from domain.entities.vacancy_response import VacancyResponse
from domain.entities.websocket_event import WebSocketEvent


class EventPublisherPort(ABC):
    """Порт для публикации событий в шину событий.
    
    Инфраструктура должна реализовать этот интерфейс.
    """

    @abstractmethod
    async def publish(self, event: WebSocketEvent) -> None:
        """Опубликовать событие в шину событий.
        
        Args:
            event: Событие для публикации.
        """

    @abstractmethod
    async def publish_agent_action_created(
        self, action: AgentAction
    ) -> None:
        """Опубликовать событие о создании AgentAction.
        
        Args:
            action: Созданное действие агента.
        """

    @abstractmethod
    async def publish_vacancy_response_created(
        self, response: VacancyResponse
    ) -> None:
        """Опубликовать событие о создании VacancyResponse.
        
        Args:
            response: Созданный отклик на вакансию.
        """
