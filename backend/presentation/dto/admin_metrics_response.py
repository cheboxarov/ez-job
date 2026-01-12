"""DTO для ответов админских метрик."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class LlmPeriodMetric(BaseModel):
    """Метрика LLM за период."""

    period_start: datetime = Field(..., description="Начало периода")
    calls_count: int = Field(..., description="Количество вызовов")
    total_tokens: int = Field(..., description="Суммарные токены")
    unique_users: int = Field(..., description="Количество уникальных пользователей")
    total_cost: float = Field(..., description="Суммарная стоимость в USD")


class LlmTotalMetrics(BaseModel):
    """Суммарные метрики LLM."""

    calls_count: int = Field(..., description="Общее количество вызовов")
    total_tokens: int = Field(..., description="Суммарные токены")
    unique_users: int = Field(..., description="Количество уникальных пользователей")
    avg_tokens_per_user: float = Field(..., description="Средние токены на пользователя")
    total_cost: float = Field(..., description="Суммарная стоимость в USD")


class LlmUsageMetricsResponse(BaseModel):
    """Ответ с метриками использования LLM."""

    metrics_by_period: list[LlmPeriodMetric] = Field(..., description="Метрики по периодам")
    total_metrics: LlmTotalMetrics = Field(..., description="Суммарные метрики")


class VacancyResponsePeriodMetric(BaseModel):
    """Метрика откликов за период."""

    period_start: datetime = Field(..., description="Начало периода")
    responses_count: int = Field(..., description="Количество откликов")
    unique_users: int = Field(..., description="Количество уникальных пользователей")


class VacancyResponseTotalMetrics(BaseModel):
    """Суммарные метрики откликов."""

    responses_count: int = Field(..., description="Общее количество откликов")
    unique_users: int = Field(..., description="Количество уникальных пользователей")
    avg_responses_per_user: float = Field(..., description="Средние отклики на пользователя")


class VacancyResponsesMetricsResponse(BaseModel):
    """Ответ с метриками откликов на вакансии."""

    metrics_by_period: list[VacancyResponsePeriodMetric] = Field(
        ..., description="Метрики по периодам"
    )
    total_metrics: VacancyResponseTotalMetrics = Field(..., description="Суммарные метрики")


class PaidUsersMetrics(BaseModel):
    """Метрики платных пользователей."""

    paid_users_count: int = Field(..., description="Количество пользователей с платными планами")
    total_cost_for_paid_users: float = Field(
        ..., description="Общая стоимость LLM для платных пользователей"
    )
    avg_cost_per_paid_user: float = Field(
        ..., description="Средняя стоимость LLM на платного пользователя"
    )


class CombinedMetricsResponse(BaseModel):
    """Комбинированный ответ с метриками LLM и откликов."""

    llm_metrics: LlmUsageMetricsResponse = Field(..., description="Метрики LLM")
    responses_metrics: VacancyResponsesMetricsResponse = Field(
        ..., description="Метрики откликов"
    )
    paid_users_metrics: PaidUsersMetrics = Field(
        ..., description="Метрики платных пользователей"
    )