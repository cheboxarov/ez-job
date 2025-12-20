from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(slots=True)
class VacancyListItem:
    """Краткая вакансия из выдачи /search/vacancy.

    Держим только то, что реально нужно домену, остальное можно будет
    при необходимости добавить позже.
    """

    vacancy_id: int
    name: str
    area_name: Optional[str] = None
    publication_time_iso: Optional[str] = None
    
    # Дополнительные поля из API
    alternate_url: Optional[str] = None
    company_name: Optional[str] = None
    salary_from: Optional[int] = None
    salary_to: Optional[int] = None
    salary_currency: Optional[str] = None
    salary_gross: Optional[bool] = None
    schedule_name: Optional[str] = None
    snippet_requirement: Optional[str] = None
    snippet_responsibility: Optional[str] = None
    vacancy_type_name: Optional[str] = None
    response_letter_required: Optional[bool] = None
    has_test: Optional[bool] = None
    address_city: Optional[str] = None
    address_street: Optional[str] = None
    professional_roles: Optional[List[str]] = None


@dataclass(slots=True)
class VacancyList:
    """Агрегат списка вакансий."""

    items: List[VacancyListItem]
