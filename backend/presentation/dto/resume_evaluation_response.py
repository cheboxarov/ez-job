from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class ResumeEvaluationRemark(BaseModel):
    """Замечание по резюме."""
    rule: str = Field(..., description="Название правила")
    comment: str = Field(..., description="Комментарий к ошибке")
    improvement: str = Field(..., description="Как исправить")


class ResumeEvaluationResponse(BaseModel):
    """Результат оценки резюме."""
    conf: float = Field(..., description="Оценка резюме от 0.0 до 1.0")
    remarks: List[ResumeEvaluationRemark] = Field(default_factory=list, description="Список замечаний")
    summary: Optional[str] = Field(None, description="Общее резюме по документу")
