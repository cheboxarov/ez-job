"""Интерфейс для агента анализа чатов и генерации ответов."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from domain.entities.hh_chat_detailed import HHChatDetailed
from domain.entities.agent_action import AgentAction


class MessagesAgentServicePort(ABC):
    """Порт сервиса агента для анализа чатов и генерации ответов.

    Инфраструктура должна реализовать этот интерфейс.
    """

    @abstractmethod
    async def analyze_chats_and_generate_responses(
        self,
        chats: List[HHChatDetailed],
        resume: str,
        user_id: UUID,
        user_parameters: str | None = None,
        resume_hash: str | None = None,
    ) -> List[AgentAction]:
        """Анализирует чаты и генерирует ответы на вопросы.

        Анализирует последние сообщения в каждом чате, определяет наличие вопросов,
        требующих ответа, и генерирует ответы только для таких чатов.

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
        raise NotImplementedError

