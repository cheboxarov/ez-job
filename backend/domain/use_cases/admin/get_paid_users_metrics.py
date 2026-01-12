"""Use case для получения метрик платных пользователей."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain.interfaces.llm_call_repository_port import LlmCallRepositoryPort


@dataclass(slots=True)
class GetPaidUsersMetricsUseCase:
    """Use case для получения метрик платных пользователей."""

    llm_call_repository: LlmCallRepositoryPort

    async def execute(
        self,
        *,
        start_date: datetime,
        end_date: datetime,
    ) -> tuple[int, float, float]:
        """Получить метрики платных пользователей.

        Args:
            start_date: Начальная дата (включительно).
            end_date: Конечная дата (включительно).

        Returns:
            Кортеж (количество платных пользователей, общая стоимость LLM для платных пользователей,
            средняя стоимость LLM на платного пользователя).
        """
        (
            paid_users_count,
            total_prompt_tokens,
            total_completion_tokens,
            total_cost_from_db,
        ) = await self.llm_call_repository.get_paid_users_llm_metrics(
            start_date=start_date,
            end_date=end_date,
        )

        # Используем стоимость из БД напрямую
        total_cost = total_cost_from_db

        # Рассчитываем среднюю стоимость на платного пользователя
        avg_cost_per_paid_user = (
            total_cost / paid_users_count if paid_users_count > 0 else 0.0
        )

        return paid_users_count, total_cost, avg_cost_per_paid_user
