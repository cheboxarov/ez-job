"""Use case для получения метрик использования LLM."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.interfaces.llm_call_repository_port import LlmCallRepositoryPort


@dataclass(slots=True)
class GetLlmUsageMetricsUseCase:
    """Use case для получения метрик использования LLM."""

    llm_call_repository: LlmCallRepositoryPort

    async def execute(
        self,
        *,
        start_date: datetime,
        end_date: datetime,
        plan_id: UUID | None = None,
        time_step: str = "day",
    ) -> tuple[list[tuple[datetime, int, int, int, float]], tuple[int, int, int, float, float]]:
        """Получить метрики использования LLM.

        Args:
            start_date: Начальная дата (включительно).
            end_date: Конечная дата (включительно).
            plan_id: Фильтр по ID плана подписки (опционально).
            time_step: Шаг группировки ('day', 'week', 'month').

        Returns:
            Кортеж из:
            - списка метрик по периодам (дата, вызовы, токены, пользователи, стоимость)
            - суммарных метрик (вызовы, токены, пользователи, средние токены на пользователя, стоимость).
        """
        metrics_by_period = await self.llm_call_repository.get_metrics_by_period(
            start_date=start_date,
            end_date=end_date,
            plan_id=plan_id,
            time_step=time_step,
        )

        total_metrics = await self.llm_call_repository.get_total_metrics(
            start_date=start_date,
            end_date=end_date,
            plan_id=plan_id,
        )

        return metrics_by_period, total_metrics
