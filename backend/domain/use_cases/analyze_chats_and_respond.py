"""Use case для анализа чатов и генерации ответов."""

from __future__ import annotations

from typing import List
from uuid import UUID
from loguru import logger

from domain.entities.hh_chat_detailed import HHChatDetailed
from domain.entities.agent_action import AgentAction
from domain.interfaces.messages_agent_service_port import MessagesAgentServicePort


class AnalyzeChatsAndRespondUseCase:
    """Use case для анализа чатов и генерации ответов на вопросы.

    Инкапсулирует бизнес-логику анализа чатов через агента.
    """

    def __init__(
        self,
        messages_agent_service: MessagesAgentServicePort,
    ) -> None:
        """Инициализация use case.

        Args:
            messages_agent_service: Сервис агента для анализа чатов и генерации ответов.
        """
        self._messages_agent_service = messages_agent_service

    async def execute(
        self,
        chats: List[HHChatDetailed],
        resume: str,
        user_id: UUID,
        user_parameters: str | None = None,
        resume_hash: str | None = None,
    ) -> List[AgentAction]:
        """Анализирует чаты и генерирует ответы на вопросы.

        Args:
            chats: Список чатов с детальной информацией и сообщениями.
            resume: Текст резюме кандидата для контекста при генерации ответов.
            user_id: ID пользователя, для которого создаются действия.
            user_parameters: Дополнительные параметры пользователя для контекста (опционально).
            resume_hash: Hash резюме, использованного при создании действий (опционально).

        Returns:
            Список действий для отправки сообщений в чаты с вопросами.
            Если в чатах нет вопросов, возвращает пустой список.
        """
        if not chats:
            return []

        if not resume or not resume.strip():
            logger.warning("[usecase] Резюме не предоставлено, пропускаем анализ чатов")
            return []

        try:
            actions = await self._messages_agent_service.analyze_chats_and_generate_responses(
                chats=chats,
                resume=resume,
                user_id=user_id,
                user_parameters=user_parameters,
                resume_hash=resume_hash,
            )
            return actions
        except Exception as exc:  # pragma: no cover - диагностический путь
            logger.error(f"[usecase] Ошибка при анализе чатов: {exc}", exc_info=True)
            return []

