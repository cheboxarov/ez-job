from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from domain.entities.filtered_vacancy import FilteredVacancyDetailWithCoverLetter


class VacancyResponse(BaseModel):
    """DTO для представления вакансии в JSON ответе."""

    vacancy_id: int
    name: str
    company_name: str | None = None
    area_name: str | None = None
    compensation: str | None = None
    publication_date: str | None = None
    work_experience: str | None = None
    employment: str | None = None
    work_formats: List[str] | None = None
    schedule_by_days: List[str] | None = None
    working_hours: List[str] | None = None
    link: str | None = None
    key_skills: List[str] | None = None
    description_html: str | None = None
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    reason: str | None = None
    cover_letter: str | None = None

    @classmethod
    def from_entity(
        cls, vacancy: FilteredVacancyDetailWithCoverLetter
    ) -> "VacancyResponse":
        """Создает DTO из сущности вакансии.

        Args:
            vacancy: Сущность вакансии с сопроводительным письмом.

        Returns:
            DTO для JSON ответа.
        """
        return cls(
            vacancy_id=vacancy.vacancy_id,
            name=vacancy.name,
            company_name=vacancy.company_name,
            area_name=vacancy.area_name,
            compensation=vacancy.compensation,
            publication_date=vacancy.publication_date,
            work_experience=vacancy.work_experience,
            employment=vacancy.employment,
            work_formats=vacancy.work_formats,
            schedule_by_days=vacancy.schedule_by_days,
            working_hours=vacancy.working_hours,
            link=vacancy.link,
            key_skills=vacancy.key_skills,
            description_html=vacancy.description_html,
            confidence=vacancy.confidence,
            reason=vacancy.reason,
            cover_letter=vacancy.cover_letter,
        )


class VacanciesResponse(BaseModel):
    """DTO для ответа со списком вакансий."""

    count: int = Field(..., description="Количество вакансий")
    items: List[VacancyResponse] = Field(..., description="Список вакансий")

