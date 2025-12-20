from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(slots=True)
class HHResume:
    """Резюме пользователя из HH API /applicant/resumes.
    
    Основная сущность для работы с резюме соискателя в HH.
    """

    resume_id: str
    hash: str
    title: str
    
    status: Optional[str] = None
    area_name: Optional[str] = None
    salary_amount: Optional[int] = None
    salary_currency: Optional[str] = None
    is_searchable: bool = True
    key_skills: List[str] | None = None
    professional_role_id: Optional[int] = None
    total_experience_months: Optional[int] = None
    updated_timestamp: Optional[int] = None
    created_timestamp: Optional[int] = None
    last_edit_time: Optional[int] = None
