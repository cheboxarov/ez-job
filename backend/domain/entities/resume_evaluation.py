"""Доменная сущность оценки резюме."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
from uuid import UUID


@dataclass
class ResumeEvaluation:
    """Доменная сущность оценки резюме.

    Хранит результат оценки резюме от LLM для кеширования.
    """

    id: UUID
    resume_content_hash: str
    evaluation_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
