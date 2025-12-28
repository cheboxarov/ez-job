"""Интерфейс для подписки на события."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator

from domain.entities.websocket_event import WebSocketEvent
from uuid import UUID


class EventSubscriberPort(ABC):
    """Порт для подписки на события из шины событий.
    
    Инфраструктура должна реализовать этот интерфейс.
    """

    @abstractmethod
    async def subscribe(self, user_id: UUID) -> AsyncIterator[WebSocketEvent]:
        """Подписаться на события для конкретного пользователя.
        
        Args:
            user_id: ID пользователя, для которого нужно получать события.
            
        Yields:
            События для указанного пользователя.
        """

    @abstractmethod
    async def unsubscribe(self, user_id: UUID, queue_id: str | None = None) -> None:
        """Отписаться от событий.
        
        Args:
            user_id: ID пользователя.
            queue_id: Опциональный идентификатор очереди для отписки конкретной подписки.
                     Если None, отписываются все подписки пользователя.
        """
