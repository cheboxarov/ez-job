"""DTO для запросов резюме."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


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
    autolike_threshold: int | None = Field(
        None, description="Порог автолика в процентах (0-100)"
    )

    @field_validator("autolike_threshold")
    @classmethod
    def validate_autolike_threshold(cls, v: int | None) -> int | None:
        """Валидация порога автолика."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError("autolike_threshold должен быть в диапазоне от 0 до 100")
        return v


class EditHHResumeExperienceItem(BaseModel):
    """DTO для одного элемента опыта работы при редактировании резюме на HH."""

    id: int = Field(..., description="ID опыта работы")
    startDate: str = Field(..., description="Дата начала работы в формате YYYY-MM-DD")
    endDate: Optional[str] = Field(None, description="Дата окончания работы в формате YYYY-MM-DD или null")
    companyName: str = Field(..., description="Название компании")
    position: str = Field(..., description="Должность")
    description: Optional[str] = Field(None, description="Описание обязанностей и достижений")
    companyIndustryId: Optional[int] = Field(None, description="ID отрасли компании")
    companyIndustries: Optional[List[int]] = Field(None, description="Список ID отраслей компании")
    companyAreaId: Optional[int] = Field(None, description="ID региона компании")
    industries: Optional[List[int]] = Field(None, description="Список ID отраслей")
    companyUrl: Optional[str] = Field(None, description="URL компании")
    companyId: Optional[int] = Field(None, description="ID компании")
    employerId: Optional[int] = Field(None, description="ID работодателя")
    companyState: Optional[str] = Field(None, description="Статус компании")
    professionId: Optional[int] = Field(None, description="ID профессии")
    professionName: Optional[str] = Field(None, description="Название профессии")

    class Config:
        """Конфигурация Pydantic."""

        json_schema_extra = {
            "example": {
                "id": 1818776055,
                "startDate": "2024-01-01",
                "endDate": None,
                "companyName": "FlowAI",
                "position": "Python-разработчик",
                "description": "Разработка backend-сервисов...",
            }
        }


class EditHHResumeRequest(BaseModel):
    """DTO для редактирования резюме на HeadHunter."""

    experience: List[EditHHResumeExperienceItem] = Field(
        ..., description="Список опыта работы для обновления"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь для отправки в HH API."""
        return {
            "experience": [item.model_dump(exclude_none=True) for item in self.experience]
        }