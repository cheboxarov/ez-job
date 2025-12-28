"""DTO для ответов резюме."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from domain.entities.resume import Resume


class ResumeResponse(BaseModel):
    """DTO для представления резюме в JSON ответе."""

    id: UUID = Field(..., description="UUID резюме")
    user_id: UUID = Field(..., description="UUID пользователя")
    content: str = Field(..., description="Текст резюме")
    user_parameters: str | None = Field(
        None, description="Дополнительные параметры фильтрации"
    )
    external_id: str | None = Field(
        None, description="Внешний ID резюме (например, ID из HeadHunter)"
    )
    headhunter_hash: str | None = Field(
        None, description="Hash резюме из HeadHunter для откликов"
    )
    is_auto_reply: bool = Field(
        False, description="Включен ли автоматический отклик на вакансии"
    )
    autolike_threshold: int = Field(
        50, description="Порог автолика в процентах (0-100)"
    )

    @classmethod
    def from_entity(cls, resume: Resume) -> "ResumeResponse":
        """Создает DTO из доменной сущности резюме.

        Args:
            resume: Доменная сущность Resume.

        Returns:
            DTO для JSON ответа.
        """
        return cls(
            id=resume.id,
            user_id=resume.user_id,
            content=resume.content,
            user_parameters=resume.user_parameters,
            external_id=resume.external_id,
            headhunter_hash=resume.headhunter_hash,
            is_auto_reply=resume.is_auto_reply,
            autolike_threshold=resume.autolike_threshold,
        )


class ResumesListResponse(BaseModel):
    """DTO для ответа со списком резюме."""

    count: int = Field(..., description="Количество резюме")
    items: list[ResumeResponse] = Field(..., description="Список резюме")
