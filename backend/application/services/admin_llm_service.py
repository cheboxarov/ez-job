"""Сервис приложения для админских операций с метриками и логами LLM."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from domain.entities.llm_call import LlmCall
from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from domain.use_cases.admin.get_llm_call_detail import GetLlmCallDetailUseCase
from domain.use_cases.admin.get_llm_usage_metrics import GetLlmUsageMetricsUseCase
from domain.use_cases.admin.get_paid_users_metrics import GetPaidUsersMetricsUseCase
from domain.use_cases.admin.get_vacancy_responses_metrics import (
    GetVacancyResponsesMetricsUseCase,
)
from domain.use_cases.admin.list_llm_calls_for_admin import ListLlmCallsForAdminUseCase


class AdminLlmService:
    """Сервис, оркестрирующий админские use case-ы по метрикам и логам LLM."""

    def __init__(self, unit_of_work: UnitOfWorkPort) -> None:
        self._unit_of_work = unit_of_work

    async def get_llm_usage_metrics(
        self,
        *,
        start_date: datetime,
        end_date: datetime,
        plan_id: UUID | None = None,
        time_step: str = "day",
    ) -> tuple[list[tuple[datetime, int, int, int]], tuple[int, int, int, float]]:
        """Получить метрики использования LLM."""
        async with self._unit_of_work:
            use_case = GetLlmUsageMetricsUseCase(
                llm_call_repository=self._unit_of_work.standalone_llm_call_repository,
            )
            return await use_case.execute(
                start_date=start_date,
                end_date=end_date,
                plan_id=plan_id,
                time_step=time_step,
            )

    async def get_vacancy_responses_metrics(
        self,
        *,
        start_date: datetime,
        end_date: datetime,
        plan_id: UUID | None = None,
        time_step: str = "day",
    ) -> tuple[list[tuple[datetime, int, int]], tuple[int, int, float]]:
        """Получить метрики откликов на вакансии."""
        async with self._unit_of_work:
            use_case = GetVacancyResponsesMetricsUseCase(
                vacancy_response_repository=self._unit_of_work.standalone_vacancy_response_repository,
            )
            return await use_case.execute(
                start_date=start_date,
                end_date=end_date,
                plan_id=plan_id,
                time_step=time_step,
            )

    async def list_llm_calls(
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
        """Получить список вызовов LLM для админки."""
        async with self._unit_of_work:
            use_case = ListLlmCallsForAdminUseCase(
                llm_call_repository=self._unit_of_work.standalone_llm_call_repository,
            )
            return await use_case.execute(
                start_date=start_date,
                end_date=end_date,
                user_id=user_id,
                agent_name=agent_name,
                status=status,
                page=page,
                page_size=page_size,
            )

    async def get_llm_call_detail(self, call_id: UUID) -> LlmCall | None:
        """Получить детальную информацию о вызове LLM."""
        async with self._unit_of_work:
            use_case = GetLlmCallDetailUseCase(
                llm_call_repository=self._unit_of_work.standalone_llm_call_repository,
            )
            return await use_case.execute(call_id)

    async def get_paid_users_metrics(
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
        async with self._unit_of_work:
            use_case = GetPaidUsersMetricsUseCase(
                llm_call_repository=self._unit_of_work.standalone_llm_call_repository,
            )
            return await use_case.execute(
                start_date=start_date,
                end_date=end_date,
            )
