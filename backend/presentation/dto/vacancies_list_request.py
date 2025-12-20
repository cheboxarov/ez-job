from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class VacanciesListRequest(BaseModel):
    """DTO для запроса релевантных list-вакансий.

    Клиент должен передать resume_id для использования резюме.
    search_session_id генерируется автоматически в сервисе.
    """

    resume_id: UUID = Field(..., description="UUID резюме для использования при поиске вакансий")
    page_indices: Optional[List[int]] = Field(
        None, min_items=1, description="Список индексов страниц (если не задан, используется дефолт из конфига)",
    )
    min_confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Минимальный порог confidence (если не задан, используется из конфига)"
    )
    order_by: str | None = Field(None, description="Опциональный параметр сортировки")

