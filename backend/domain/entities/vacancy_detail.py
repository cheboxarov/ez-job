from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(slots=True)
class VacancyDetail:
    """Детальная информация по вакансии на основе блока vacancyView."""

    vacancy_id: int
    name: str

    company_name: Optional[str] = None
    area_name: Optional[str] = None

    compensation: Optional[str] = None
    publication_date: Optional[str] = None

    work_experience: Optional[str] = None
    employment: Optional[str] = None

    work_formats: List[str] | None = None
    schedule_by_days: List[str] | None = None
    working_hours: List[str] | None = None

    link: Optional[str] = None

    key_skills: List[str] | None = None
    description_html: Optional[str] = None
