"""Сервис для управления WebSocket соединениями."""

from __future__ import annotations

import asyncio
import json
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger

from domain.interfaces.event_subscriber_port import EventSubscriberPort
from infrastructure.websocket.websocket_manager import WebSocketManager


class WebSocketService:
    """Сервис для управления WebSocket соединениями.
    
    Обрабатывает подключения, подписки на события и отправку событий в WebSocket.
    """

    def __init__(
        self,
        websocket_manager: WebSocketManager,
        event_subscriber: EventSubscriberPort,
    ) -> None:
        """Инициализация сервиса.
        
        Args:
            websocket_manager: Менеджер WebSocket соединений.
            event_subscriber: Подписчик на события из Event Bus.
        """
        self._websocket_manager = websocket_manager
        self._event_subscriber = event_subscriber

    async def handle_connection(
        self, websocket: WebSocket, user_id: UUID
    ) -> None:
        """Обрабатывает WebSocket соединение пользователя.
        
        Args:
            websocket: WebSocket соединение.
            user_id: ID пользователя.
        """
        # 1. Принимаем соединение
        await websocket.accept()
        logger.info(f"WebSocket соединение принято для пользователя {user_id}")
        
        # 2. Регистрируем соединение в менеджере
        await self._websocket_manager.connect(websocket, user_id)
        
        try:
            # 3. Подписываемся на события и отправляем их в WebSocket
            async for event in self._event_subscriber.subscribe(user_id):
                try:
                    event_dict = {
                        "event_type": event.event_type,
                        "payload": event.payload,
                        "created_at": event.created_at.isoformat(),
                    }
                    await websocket.send_json(event_dict)
                    logger.debug(
                        f"Событие {event.event_type} отправлено в WebSocket для пользователя {user_id}"
                    )
                except WebSocketDisconnect:
                    logger.info(f"WebSocket соединение закрыто клиентом для пользователя {user_id}")
                    break
                except Exception as exc:
                    logger.error(
                        f"Ошибка при отправке события в WebSocket для пользователя {user_id}: {exc}",
                        exc_info=True,
                    )
                    # Продолжаем обработку событий даже при ошибке отправки
        except asyncio.CancelledError:
            logger.info(f"Подписка на события отменена для пользователя {user_id}")
        except Exception as exc:
            logger.error(
                f"Ошибка в обработке WebSocket соединения для пользователя {user_id}: {exc}",
                exc_info=True,
            )
        finally:
            # 4. Отключаем соединение при выходе
            await self._websocket_manager.disconnect(websocket, user_id)
            logger.info(f"WebSocket соединение закрыто для пользователя {user_id}")
