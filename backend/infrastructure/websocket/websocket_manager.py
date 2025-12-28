"""Менеджер для управления WebSocket соединениями."""

from __future__ import annotations

import asyncio
from typing import Dict, Set
from uuid import UUID

from fastapi import WebSocket
from loguru import logger

from domain.entities.websocket_event import WebSocketEvent


class WebSocketManager:
    """Менеджер для управления WebSocket соединениями.
    
    Хранит активные соединения и отправляет события в WebSocket.
    """

    def __init__(self) -> None:
        """Инициализация WebSocket Manager."""
        self._connections: Dict[UUID, Set[WebSocket]] = {}
        """Словарь активных соединений: user_id -> Set[WebSocket]."""
        self._lock = asyncio.Lock()
        """Lock для thread-safe операций."""

    async def connect(self, websocket: WebSocket, user_id: UUID) -> None:
        """Подключить WebSocket соединение.
        
        Args:
            websocket: WebSocket соединение.
            user_id: ID пользователя.
        """
        async with self._lock:
            if user_id not in self._connections:
                self._connections[user_id] = set()
            self._connections[user_id].add(websocket)
            logger.info(
                f"WebSocket подключен: user_id={user_id}, "
                f"всего соединений для пользователя: {len(self._connections[user_id])}"
            )

    async def disconnect(self, websocket: WebSocket, user_id: UUID) -> None:
        """Отключить WebSocket соединение.
        
        Args:
            websocket: WebSocket соединение.
            user_id: ID пользователя.
        """
        async with self._lock:
            if user_id in self._connections:
                self._connections[user_id].discard(websocket)
                logger.info(
                    f"WebSocket отключен: user_id={user_id}, "
                    f"осталось соединений: {len(self._connections[user_id])}"
                )
                # Если соединений не осталось, удаляем пользователя из словаря
                if not self._connections[user_id]:
                    self._connections.pop(user_id, None)

    async def send_event(self, event: WebSocketEvent) -> None:
        """Отправить событие во все WebSocket соединения пользователя.
        
        Args:
            event: Событие для отправки.
        """
        async with self._lock:
            connections = self._connections.get(event.user_id, set()).copy()
        
        if not connections:
            logger.debug(
                f"Нет активных WebSocket соединений для пользователя {event.user_id}, "
                f"событие {event.event_type} не будет отправлено"
            )
            return
        
        # Отправляем событие во все соединения пользователя
        disconnected = set()
        for websocket in connections:
            try:
                event_dict = {
                    "event_type": event.event_type,
                    "payload": event.payload,
                    "created_at": event.created_at.isoformat(),
                }
                await websocket.send_json(event_dict)
                logger.debug(
                    f"Событие {event.event_type} отправлено в WebSocket "
                    f"для пользователя {event.user_id}"
                )
            except Exception as exc:
                logger.warning(
                    f"Ошибка при отправке события в WebSocket для пользователя {event.user_id}: {exc}"
                )
                disconnected.add(websocket)
        
        # Удаляем отключенные соединения
        if disconnected:
            async with self._lock:
                if event.user_id in self._connections:
                    self._connections[event.user_id] -= disconnected
                    if not self._connections[event.user_id]:
                        self._connections.pop(event.user_id, None)
