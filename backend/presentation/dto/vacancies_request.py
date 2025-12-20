from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class VacanciesRequest(BaseModel):
    """DTO для запроса релевантных вакансий.

    Клиент должен передать resume_id для использования резюме.
    search_session_id генерируется автоматически в сервисе.
    """

    resume_id: UUID = Field(..., description="UUID резюме для использования при поиске вакансий")
    page_indices: Optional[List[int]] = Field(
        None, min_items=1, description="Список индексов страниц (если не задан, используется дефолт из конфига)",
    )
    min_confidence_for_cover_letter: float = Field(
        ..., ge=0.0, le=1.0, description="Минимальный порог confidence для генерации письма"
    )
    order_by: str | None = Field(None, description="Опциональный параметр сортировки")

