"""DTO для ответа со списком откликов на вакансии."""

from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field

from domain.entities.vacancy_response import VacancyResponse


class VacancyResponseItem(BaseModel):
    """DTO для одного отклика на вакансию."""

    id: UUID = Field(..., description="UUID отклика")
    vacancy_id: int = Field(..., description="ID вакансии в HeadHunter")
    vacancy_name: str = Field(..., description="Название вакансии")
    vacancy_url: str | None = Field(None, description="URL вакансии")
    cover_letter: str = Field(..., description="Текст сопроводительного письма")
    created_at: datetime = Field(..., description="Дата и время создания отклика")

    @classmethod
    def from_entity(cls, vacancy_response: VacancyResponse) -> "VacancyResponseItem":
        """Создает DTO из доменной сущности.

        Args:
            vacancy_response: Доменная сущность VacancyResponse.

        Returns:
            DTO для JSON ответа.
        """
        return cls(
            id=vacancy_response.id,
            vacancy_id=vacancy_response.vacancy_id,
            vacancy_name=vacancy_response.vacancy_name,
            vacancy_url=vacancy_response.vacancy_url,
            cover_letter=vacancy_response.cover_letter,
            created_at=vacancy_response.created_at or datetime.utcnow(),
        )


class VacancyResponsesListResponse(BaseModel):
    """DTO для ответа со списком откликов с пагинацией."""

    items: List[VacancyResponseItem] = Field(..., description="Список откликов")
    total: int = Field(..., description="Общее количество откликов")
    offset: int = Field(..., description="Смещение для пагинации")
    limit: int = Field(..., description="Количество записей на странице")
