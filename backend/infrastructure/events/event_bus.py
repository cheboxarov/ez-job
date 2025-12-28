"""In-memory Event Bus для публикации и подписки на события."""

from __future__ import annotations

import asyncio
import uuid
from typing import AsyncIterator, Dict, Set
from uuid import UUID

from loguru import logger

from domain.entities.websocket_event import WebSocketEvent
from domain.interfaces.event_subscriber_port import EventSubscriberPort


class EventBus(EventSubscriberPort):
    """In-memory Event Bus для публикации и подписки на события.
    
    Использует asyncio.Queue для каждого пользователя.
    Thread-safe через asyncio.Lock.
    """

    def __init__(self) -> None:
        """Инициализация Event Bus."""
        self._subscribers: Dict[UUID, Dict[str, asyncio.Queue[WebSocketEvent]]] = {}
        """Словарь подписчиков: user_id -> {queue_id -> Queue}."""
        self._lock = asyncio.Lock()
        """Lock для thread-safe операций."""

    async def publish(self, event: WebSocketEvent) -> None:
        """Опубликовать событие в шину событий.
        
        Args:
            event: Событие для публикации.
        """
        async with self._lock:
            user_subscribers = self._subscribers.get(event.user_id, {})
            
            if not user_subscribers:
                logger.debug(
                    f"Нет подписчиков для пользователя {event.user_id}, "
                    f"событие {event.event_type} будет проигнорировано"
                )
                return
            
            # Отправляем событие во все очереди подписчиков
            for queue_id, queue in user_subscribers.items():
                try:
                    queue.put_nowait(event)
                    logger.debug(
                        f"Событие {event.event_type} отправлено в очередь {queue_id} "
                        f"для пользователя {event.user_id}"
                    )
                except asyncio.QueueFull:
                    logger.warning(
                        f"Очередь {queue_id} для пользователя {event.user_id} переполнена, "
                        f"событие {event.event_type} потеряно"
                    )

    async def subscribe(self, user_id: UUID) -> AsyncIterator[WebSocketEvent]:
        """Подписаться на события для конкретного пользователя.
        
        Args:
            user_id: ID пользователя, для которого нужно получать события.
            
        Yields:
            События для указанного пользователя.
        """
        # Создаём уникальный ID для этой подписки
        queue_id = str(uuid.uuid4())
        queue: asyncio.Queue[WebSocketEvent] = asyncio.Queue(maxsize=100)
        
        # Регистрируем подписку
        async with self._lock:
            if user_id not in self._subscribers:
                self._subscribers[user_id] = {}
            self._subscribers[user_id][queue_id] = queue
            logger.info(
                f"Подписка создана: user_id={user_id}, queue_id={queue_id}, "
                f"всего подписок для пользователя: {len(self._subscribers[user_id])}"
            )
        
        try:
            # В цикле получаем события из очереди
            while True:
                try:
                    event = await queue.get()
                    yield event
                    queue.task_done()
                except asyncio.CancelledError:
                    logger.info(f"Подписка {queue_id} для пользователя {user_id} отменена")
                    break
        finally:
            # Отписываемся при выходе
            await self.unsubscribe(user_id, queue_id)

    async def unsubscribe(self, user_id: UUID, queue_id: str | None = None) -> None:
        """Отписаться от событий.
        
        Args:
            user_id: ID пользователя.
            queue_id: Опциональный идентификатор очереди для отписки конкретной подписки.
                     Если None, отписываются все подписки пользователя.
        """
        async with self._lock:
            if user_id not in self._subscribers:
                return
            
            if queue_id is None:
                # Отписываем все подписки пользователя
                self._subscribers.pop(user_id, None)
                logger.info(f"Все подписки для пользователя {user_id} удалены")
            else:
                # Отписываем конкретную подписку
                user_subscribers = self._subscribers[user_id]
                if queue_id in user_subscribers:
                    user_subscribers.pop(queue_id)
                    logger.info(
                        f"Подписка {queue_id} для пользователя {user_id} удалена, "
                        f"осталось подписок: {len(user_subscribers)}"
                    )
                    # Если подписок не осталось, удаляем пользователя из словаря
                    if not user_subscribers:
                        self._subscribers.pop(user_id, None)
