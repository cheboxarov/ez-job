"""Use case для анализа чатов и генерации ответов."""

from __future__ import annotations

from typing import List

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
    ) -> List[AgentAction]:
        """Анализирует чаты и генерирует ответы на вопросы.

        Args:
            chats: Список чатов с детальной информацией и сообщениями.
            resume: Текст резюме кандидата для контекста при генерации ответов.

        Returns:
            Список действий для отправки сообщений в чаты с вопросами.
            Если в чатах нет вопросов, возвращает пустой список.
        """
        if not chats:
            return []

        if not resume or not resume.strip():
            print("[usecase] Резюме не предоставлено, пропускаем анализ чатов", flush=True)
            return []

        try:
            actions = await self._messages_agent_service.analyze_chats_and_generate_responses(
                chats=chats,
                resume=resume,
            )
            return actions
        except Exception as exc:  # pragma: no cover - диагностический путь
            print(f"[usecase] Ошибка при анализе чатов: {exc}", flush=True)
            return []

