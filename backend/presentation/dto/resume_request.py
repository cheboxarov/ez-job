"""DTO для запросов резюме."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CreateResumeRequest(BaseModel):
    """DTO для создания резюме."""

    content: str = Field(..., description="Текст резюме")
    user_parameters: str | None = Field(
        None, description="Дополнительные параметры фильтрации"
    )


class UpdateResumeRequest(BaseModel):
    """DTO для обновления резюме."""

    content: str | None = Field(None, description="Текст резюме")
    user_parameters: str | None = Field(
        None, description="Дополнительные параметры фильтрации"
    )
    is_auto_reply: bool | None = Field(
        None, description="Включен ли автоматический отклик на вакансии"
    )
