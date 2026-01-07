"""Use case для получения метрик откликов на вакансии."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.interfaces.vacancy_response_repository_port import (
    VacancyResponseRepositoryPort,
)


@dataclass(slots=True)
class GetVacancyResponsesMetricsUseCase:
    """Use case для получения метрик откликов на вакансии."""

    vacancy_response_repository: VacancyResponseRepositoryPort

    async def execute(
        self,
        *,
        start_date: datetime,
        end_date: datetime,
        plan_id: UUID | None = None,
        time_step: str = "day",
    ) -> tuple[list[tuple[datetime, int, int]], tuple[int, int, float]]:
        """Получить метрики откликов на вакансии.

        Args:
            start_date: Начальная дата (включительно).
            end_date: Конечная дата (включительно).
            plan_id: Фильтр по ID плана подписки (опционально).
            time_step: Шаг группировки ('day', 'week', 'month').

        Returns:
            Кортеж из:
            - списка метрик по периодам (дата, отклики, пользователи)
            - суммарных метрик (отклики, пользователи, средние отклики на пользователя).
        """
        metrics_by_period = await self.vacancy_response_repository.get_metrics_by_period(
            start_date=start_date,
            end_date=end_date,
            plan_id=plan_id,
            time_step=time_step,
        )

        total_metrics = await self.vacancy_response_repository.get_total_metrics(
            start_date=start_date,
            end_date=end_date,
            plan_id=plan_id,
        )

        return metrics_by_period, total_metrics
