"""Use case для получения списка вызовов LLM для админки."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.entities.llm_call import LlmCall
from domain.interfaces.llm_call_repository_port import LlmCallRepositoryPort


@dataclass(slots=True)
class ListLlmCallsForAdminUseCase:
    """Use case для получения списка вызовов LLM для админки."""

    llm_call_repository: LlmCallRepositoryPort

    async def execute(
        self,
        *,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        user_id: UUID | None = None,
        agent_name: str | None = None,
        status: str | None = None,
        page: int,
        page_size: int,
    ) -> tuple[list[LlmCall], int]:
        """Получить список вызовов LLM для админки.

        Args:
            start_date: Начальная дата фильтра (включительно).
            end_date: Конечная дата фильтра (включительно).
            user_id: Фильтр по ID пользователя.
            agent_name: Фильтр по имени агента.
            status: Фильтр по статусу ('success' или 'error').
            page: Номер страницы (начиная с 1).
            page_size: Размер страницы.

        Returns:
            Кортеж из списка LlmCall и общего количества записей.
        """
        return await self.llm_call_repository.list_for_admin(
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            agent_name=agent_name,
            status=status,
            page=page,
            page_size=page_size,
        )
