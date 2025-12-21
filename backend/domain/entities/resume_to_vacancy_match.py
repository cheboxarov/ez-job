"""Доменная сущность мэтча резюме-вакансия."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class ResumeToVacancyMatch:
    """Доменная сущность мэтча резюме-вакансия.

    Хранит результат нейронной фильтрации вакансии для конкретного резюме.
    Используется для кэширования результатов, чтобы избежать повторных запросов к нейросети.
    """

    resume_id: UUID
    vacancy_hash: str
    confidence: float
    reason: str | None = None
