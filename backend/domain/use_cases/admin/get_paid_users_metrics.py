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
        input_price_per_million: float = 0.0,
        output_price_per_million: float = 0.0,
    ) -> tuple[int, float, float]:
        """Получить метрики платных пользователей.

        Args:
            start_date: Начальная дата (включительно).
            end_date: Конечная дата (включительно).
            input_price_per_million: Стоимость входных токенов за миллион.
            output_price_per_million: Стоимость выходных токенов за миллион.

        Returns:
            Кортеж (количество платных пользователей, общая стоимость LLM для платных пользователей,
            средняя стоимость LLM на платного пользователя).
        """
        (
            paid_users_count,
            total_prompt_tokens,
            total_completion_tokens,
        ) = await self.llm_call_repository.get_paid_users_llm_metrics(
            start_date=start_date,
            end_date=end_date,
        )

        # Рассчитываем стоимость
        prompt_cost = (
            (total_prompt_tokens / 1_000_000) * input_price_per_million
            if input_price_per_million > 0
            else 0.0
        )
        completion_cost = (
            (total_completion_tokens / 1_000_000) * output_price_per_million
            if output_price_per_million > 0
            else 0.0
        )
        total_cost = prompt_cost + completion_cost

        # Рассчитываем среднюю стоимость на платного пользователя
        avg_cost_per_paid_user = (
            total_cost / paid_users_count if paid_users_count > 0 else 0.0
        )

        return paid_users_count, total_cost, avg_cost_per_paid_user
