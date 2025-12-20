"""DTO для настроек фильтров поиска вакансий резюме."""

from __future__ import annotations

from typing import List
from uuid import UUID

from pydantic import BaseModel, Field

from domain.entities.resume_filter_settings import ResumeFilterSettings


class ResumeFilterSettingsResponse(BaseModel):
    """Схема настроек фильтров, возвращаемая с бэкенда."""

    resume_id: UUID

    text: str | None = Field(None, description="Поисковый текст")
    hh_resume_id: str | None = Field(
        None, description="ID резюме в HH, если нужно фильтровать по нему"
    )

    experience: List[str] | None = Field(
        None, description="Опыт работы (ids из /dictionaries/experience)"
    )
    employment: List[str] | None = Field(
        None, description="Тип занятости (ids из /dictionaries/employment)"
    )
    schedule: List[str] | None = Field(None, description="График работы (ids из /dictionaries/schedule)")
    professional_role: List[str] | None = Field(
        None, description="Профессиональные роли (ids из /professional_roles)"
    )

    area: str | None = Field(None, description="Регион (id из /areas)")
    salary: int | None = Field(None, description="Минимальная желаемая зарплата")
    currency: str | None = Field(None, description="Код валюты (RUR, USD, EUR, ...)")
    only_with_salary: bool = Field(False, description="Только вакансии с указанной зарплатой")

    order_by: str | None = Field(None, description="Сортировка (vacancy_search_order)")
    period: int | None = Field(
        None,
        description="Количество дней, за которые искать вакансии (альтернатива date_from/date_to)",
    )
    date_from: str | None = Field(None, description="Нижняя граница даты публикации (ISO 8601)")
    date_to: str | None = Field(None, description="Верхняя граница даты публикации (ISO 8601)")

    @classmethod
    def from_entity(cls, settings: ResumeFilterSettings) -> "ResumeFilterSettingsResponse":
        """Создает DTO из доменной сущности настроек фильтров.

        Args:
            settings: Доменная сущность ResumeFilterSettings.

        Returns:
            DTO для JSON ответа.
        """
        return cls(
            resume_id=settings.resume_id,
            text=settings.text,
            hh_resume_id=settings.hh_resume_id,
            experience=settings.experience,
            employment=settings.employment,
            schedule=settings.schedule,
            professional_role=settings.professional_role,
            area=settings.area,
            salary=settings.salary,
            currency=settings.currency,
            only_with_salary=settings.only_with_salary,
            order_by=settings.order_by,
            period=settings.period,
            date_from=settings.date_from,
            date_to=settings.date_to,
        )


class ResumeFilterSettingsUpdate(BaseModel):
    """Схема для обновления настроек фильтров резюме.

    Предполагаем, что фронт отправляет все поля формы целиком.
    """

    text: str | None = Field(None, description="Поисковый текст")
    hh_resume_id: str | None = Field(None, description="ID резюме в HH")

    experience: List[str] | None = None
    employment: List[str] | None = None
    schedule: List[str] | None = None
    professional_role: List[str] | None = None

    area: str | None = None
    salary: int | None = None
    currency: str | None = None
    only_with_salary: bool | None = None

    order_by: str | None = None
    period: int | None = None
    date_from: str | None = None
    date_to: str | None = None
