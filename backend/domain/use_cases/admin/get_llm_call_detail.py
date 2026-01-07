"""Use case для получения детальной информации о вызове LLM."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from domain.entities.llm_call import LlmCall
from domain.interfaces.llm_call_repository_port import LlmCallRepositoryPort


@dataclass(slots=True)
class GetLlmCallDetailUseCase:
    """Use case для получения детальной информации о вызове LLM."""

    llm_call_repository: LlmCallRepositoryPort

    async def execute(self, call_id: UUID) -> LlmCall | None:
        """Получить детальную информацию о вызове LLM.

        Args:
            call_id: UUID записи о вызове LLM.

        Returns:
            Доменная сущность LlmCall или None, если не найдено.
        """
        return await self.llm_call_repository.get_by_id(call_id)
