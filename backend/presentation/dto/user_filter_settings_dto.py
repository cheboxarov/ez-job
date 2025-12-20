"""DTO для настроек фильтров поиска вакансий пользователя."""

from __future__ import annotations

from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class UserFilterSettingsResponse(BaseModel):
    """Схема настроек фильтров, возвращаемая с бэкенда."""

    user_id: UUID

    text: str | None = Field(None, description="Поисковый текст")
    resume_id: str | None = Field(None, description="ID резюме в HH, если нужно фильтровать по нему")

    experience: List[str] | None = Field(None, description="Опыт работы (ids из /dictionaries/experience)")
    employment: List[str] | None = Field(None, description="Тип занятости (ids из /dictionaries/employment)")
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
        None, description="Количество дней, за которые искать вакансии (альтернатива date_from/date_to)",
    )
    date_from: str | None = Field(None, description="Нижняя граница даты публикации (ISO 8601)")
    date_to: str | None = Field(None, description="Верхняя граница даты публикации (ISO 8601)")


class UserFilterSettingsUpdate(BaseModel):
    """Схема для обновления настроек фильтров пользователя.

    Предполагаем, что фронт отправляет все поля формы целиком.
    """

    text: str | None = Field(None, description="Поисковый текст")
    resume_id: str | None = Field(None, description="ID резюме в HH")

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


class SuggestedUserFilterSettingsResponse(BaseModel):
    """Схема предложенных (AI) настроек фильтров.

    Содержит только те поля, которые мы автогенерируем.
    """

    text: str | None = Field(None, description="Предложенный поисковый текст")
    salary: int | None = Field(None, description="Предложенная минимальная зарплата")
    currency: str | None = Field(None, description="Предложенный код валюты")
