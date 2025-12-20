from __future__ import annotations

from dataclasses import dataclass

from domain.entities.vacancy_list import VacancyListItem


@dataclass(slots=True)
class FilteredVacancyListDto:
    """Результат работы нейронной фильтрации по одной list-вакансии (служебный DTO)."""

    vacancy_id: int
    confidence: float
    reason: str | None = None


@dataclass(slots=True)
class FilteredVacancyListItem(VacancyListItem):
    """Краткая вакансия из списка с дополнительным полем confidence.

    Наследуемся от VacancyListItem, чтобы сохранить все поля list-вакансии
    и добавить к ним только оценку соответствия.
    """

    confidence: float = 0.0
    reason: str | None = None

    @classmethod
    def from_list_item(
        cls, list_item: VacancyListItem, confidence: float, reason: str | None = None
    ) -> "FilteredVacancyListItem":
        """Удобный конструктор поверх базовой VacancyListItem."""
        return cls(
            vacancy_id=list_item.vacancy_id,
            name=list_item.name,
            area_name=list_item.area_name,
            publication_time_iso=list_item.publication_time_iso,
            alternate_url=list_item.alternate_url,
            company_name=list_item.company_name,
            salary_from=list_item.salary_from,
            salary_to=list_item.salary_to,
            salary_currency=list_item.salary_currency,
            salary_gross=list_item.salary_gross,
            schedule_name=list_item.schedule_name,
            snippet_requirement=list_item.snippet_requirement,
            snippet_responsibility=list_item.snippet_responsibility,
            vacancy_type_name=list_item.vacancy_type_name,
            response_letter_required=list_item.response_letter_required,
            has_test=list_item.has_test,
            address_city=list_item.address_city,
            address_street=list_item.address_street,
            professional_roles=list(list_item.professional_roles or []) if list_item.professional_roles else None,
            confidence=confidence,
            reason=reason,
        )

