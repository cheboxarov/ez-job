from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from domain.entities.filtered_vacancy_list import FilteredVacancyListItem


class VacancyListItemResponse(BaseModel):
    """DTO для представления list-вакансии в JSON ответе."""

    vacancy_id: int
    name: str
    area_name: str | None = None
    publication_time_iso: str | None = None
    alternate_url: str | None = None
    company_name: str | None = None
    salary_from: int | None = None
    salary_to: int | None = None
    salary_currency: str | None = None
    salary_gross: bool | None = None
    schedule_name: str | None = None
    snippet_requirement: str | None = None
    snippet_responsibility: str | None = None
    vacancy_type_name: str | None = None
    response_letter_required: bool | None = None
    has_test: bool | None = None
    address_city: str | None = None
    address_street: str | None = None
    professional_roles: List[str] | None = None
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    reason: str | None = None

    @classmethod
    def from_entity(
        cls, vacancy: FilteredVacancyListItem
    ) -> "VacancyListItemResponse":
        """Создает DTO из сущности list-вакансии.

        Args:
            vacancy: Сущность list-вакансии с оценкой релевантности.

        Returns:
            DTO для JSON ответа.
        """
        return cls(
            vacancy_id=vacancy.vacancy_id,
            name=vacancy.name,
            area_name=vacancy.area_name,
            publication_time_iso=vacancy.publication_time_iso,
            alternate_url=vacancy.alternate_url,
            company_name=vacancy.company_name,
            salary_from=vacancy.salary_from,
            salary_to=vacancy.salary_to,
            salary_currency=vacancy.salary_currency,
            salary_gross=vacancy.salary_gross,
            schedule_name=vacancy.schedule_name,
            snippet_requirement=vacancy.snippet_requirement,
            snippet_responsibility=vacancy.snippet_responsibility,
            vacancy_type_name=vacancy.vacancy_type_name,
            response_letter_required=vacancy.response_letter_required,
            has_test=vacancy.has_test,
            address_city=vacancy.address_city,
            address_street=vacancy.address_street,
            professional_roles=vacancy.professional_roles,
            confidence=vacancy.confidence,
            reason=vacancy.reason,
        )


class VacanciesListResponse(BaseModel):
    """DTO для ответа со списком list-вакансий."""

    count: int = Field(..., description="Количество вакансий")
    items: List[VacancyListItemResponse] = Field(..., description="Список вакансий")

