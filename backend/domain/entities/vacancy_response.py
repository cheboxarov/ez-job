"""Доменная сущность отклика на вакансию."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class VacancyResponse:
    """Доменная сущность отклика на вакансию.

    Хранит информацию об отклике пользователя на вакансию через HeadHunter.
    Содержит ID вакансии, резюме, пользователя и сопроводительное письмо.
    """

    id: UUID
    vacancy_id: int
    resume_id: UUID
    resume_hash: str | None
    user_id: UUID
    cover_letter: str
    vacancy_name: str
    vacancy_url: str | None = None
    created_at: datetime | None = None
    status: str = "success"
    error_status_code: int | None = None
    error_message: str | None = None