"""DTO для запроса отклика на вакансию."""

from __future__ import annotations

from pydantic import BaseModel, Field


class VacancyRespondRequest(BaseModel):
    """Запрос на отклик на вакансию.

    Args:
        vacancy_id: ID вакансии в HeadHunter.
        resume_id: ID резюме в нашей БД (для получения resume_hash).
        letter: Текст сопроводительного письма (по умолчанию "1").
    """

    vacancy_id: int = Field(..., description="ID вакансии в HeadHunter")
    resume_id: str = Field(..., description="ID резюме в нашей БД")
    letter: str = Field(default="1", description="Текст сопроводительного письма")
