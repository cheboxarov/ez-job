"""DTO для ответа со статистикой откликов."""

from __future__ import annotations

from datetime import date
from typing import List

from pydantic import BaseModel, Field


class StatisticsDataPoint(BaseModel):
    """DTO для одной точки данных статистики."""

    response_date: date = Field(..., description="Дата", alias="date")
    count: int = Field(..., description="Количество откликов за день")
    
    class Config:
        populate_by_name = True


class StatisticsResponse(BaseModel):
    """DTO для ответа со статистикой откликов."""

    data: List[StatisticsDataPoint] = Field(
        ..., description="Список данных по дням (дата, количество откликов)"
    )
