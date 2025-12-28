"""Реализация EventPublisher для публикации событий."""

from __future__ import annotations

from datetime import datetime, timezone

from domain.entities.agent_action import AgentAction
from domain.entities.vacancy_response import VacancyResponse
from domain.entities.websocket_event import WebSocketEvent
from domain.interfaces.event_publisher_port import EventPublisherPort
from infrastructure.events.event_bus import EventBus
from loguru import logger


class EventPublisher(EventPublisherPort):
    """Реализация EventPublisher для публикации событий в Event Bus."""

    def __init__(
        self,
        event_bus: EventBus,
        telegram_notification_use_case=None,
    ) -> None:
        """Инициализация EventPublisher.
        
        Args:
            event_bus: Event Bus для публикации событий.
            telegram_notification_use_case: Опциональный use case для отправки Telegram уведомлений.
        """
        self._event_bus = event_bus
        self._telegram_notification_uc = telegram_notification_use_case

    async def publish(self, event: WebSocketEvent) -> None:
        """Опубликовать событие в шину событий.
        
        Args:
            event: Событие для публикации.
        """
        await self._event_bus.publish(event)

    async def publish_agent_action_created(
        self, action: AgentAction
    ) -> None:
        """Опубликовать событие о создании AgentAction.
        
        Args:
            action: Созданное действие агента.
        """
        # Сериализуем AgentAction в словарь
        payload = {
            "id": str(action.id),
            "type": action.type,
            "entity_type": action.entity_type,
            "entity_id": action.entity_id,
            "created_by": action.created_by,
            "user_id": str(action.user_id),
            "resume_hash": action.resume_hash,
            "data": action.data,
            "created_at": action.created_at.isoformat(),
            "updated_at": action.updated_at.isoformat(),
            "is_read": action.is_read,
        }
        
        event = WebSocketEvent(
            event_type="agent_action_created",
            user_id=action.user_id,
            payload=payload,
            created_at=datetime.now(timezone.utc),
        )
        
        await self.publish(event)
        
        # Отправляем Telegram уведомление (если настроено)
        if self._telegram_notification_uc:
            try:
                await self._telegram_notification_uc.execute_for_agent_action(action)
            except Exception as exc:
                logger.error(
                    f"Ошибка при отправке Telegram уведомления для agent_action {action.id}: {exc}",
                    exc_info=True,
                )
                # Не прерываем выполнение, если отправка уведомления не удалась

    async def publish_vacancy_response_created(
        self, response: VacancyResponse
    ) -> None:
        """Опубликовать событие о создании VacancyResponse.
        
        Args:
            response: Созданный отклик на вакансию.
        """
        # Сериализуем VacancyResponse в словарь
        payload = {
            "id": str(response.id),
            "vacancy_id": response.vacancy_id,
            "resume_id": str(response.resume_id),
            "resume_hash": response.resume_hash,
            "user_id": str(response.user_id),
            "cover_letter": response.cover_letter,
            "vacancy_name": response.vacancy_name,
            "vacancy_url": response.vacancy_url,
            "created_at": response.created_at.isoformat() if response.created_at else None,
        }
        
        event = WebSocketEvent(
            event_type="vacancy_response_created",
            user_id=response.user_id,
            payload=payload,
            created_at=datetime.now(timezone.utc),
        )
        
        await self.publish(event)
        
        # Отправляем Telegram уведомление (если настроено)
        if self._telegram_notification_uc:
            try:
                await self._telegram_notification_uc.execute_for_vacancy_response(response)
            except Exception as exc:
                logger.error(
                    f"Ошибка при отправке Telegram уведомления для vacancy_response {response.id}: {exc}",
                    exc_info=True,
                )
                # Не прерываем выполнение, если отправка уведомления не удалась