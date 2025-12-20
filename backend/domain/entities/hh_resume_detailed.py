from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(slots=True)
class HHWorkExperience:
    """Опыт работы в резюме."""

    id: int
    company_name: str
    position: str
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration_years: Optional[int] = None
    duration_months: Optional[int] = None


@dataclass(slots=True)
class HHResumeDetailed:
    """Детальная информация о резюме из HH API /resume/{hash}.
    
    Расширенная версия резюме с полным опытом работы и описанием.
    """

    resume_id: str
    hash: str
    title: str
    
    # Личная информация
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    
    # Основная информация
    status: Optional[str] = None
    area_name: Optional[str] = None
    salary_amount: Optional[int] = None
    salary_currency: Optional[str] = None
    is_searchable: bool = True
    key_skills: List[str] | None = None
    professional_role_id: Optional[int] = None
    total_experience_months: Optional[int] = None
    
    # Опыт работы
    work_experience: List[HHWorkExperience] | None = None
    
    # О себе
    about: Optional[str] = None
    
    # Timestamps
    updated_timestamp: Optional[int] = None
    created_timestamp: Optional[int] = None
    last_edit_time: Optional[int] = None
