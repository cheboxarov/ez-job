"""Доменная сущность настроек фильтров поиска вакансий пользователя."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List
from uuid import UUID


@dataclass(slots=True)
class UserFilterSettings:
    """Настройки фильтров поиска вакансий, привязанные к пользователю.

    Эти настройки маппятся практически 1:1 на параметры публичного API HH `/vacancies`.
    Часть полей (period, date_from, date_to) являются взаимоисключающими – на уровне
    use case мы следим за тем, чтобы использовать либо period, либо пару дат.
    """

    user_id: UUID

    # Базовые параметры поискового запроса
    text: str | None = None
    resume_id: str | None = None

    # Мультизнаковые фильтры (хранить будем как список, а при запросе сериализовать)
    experience: List[str] | None = None
    employment: List[str] | None = None
    schedule: List[str] | None = None
    professional_role: List[str] | None = None

    # Регион и компенсация
    area: str | None = None
    salary: int | None = None
    currency: str | None = None
    only_with_salary: bool = False

    # Сортировка и временные ограничения
    order_by: str | None = None
    period: int | None = None
    date_from: str | None = None  # ISO 8601
    date_to: str | None = None  # ISO 8601


