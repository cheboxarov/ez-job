from __future__ import annotations

from dataclasses import dataclass

from domain.entities.vacancy_detail import VacancyDetail


@dataclass(slots=True)
class FilteredVacancyDto:
    """Результат работы нейронной фильтрации по одной вакансии (служебный DTO)."""

    vacancy_id: int
    confidence: float
    reason: str | None = None


@dataclass(slots=True)
class FilteredVacancyDetail(VacancyDetail):
    """Детальная вакансия с дополнительным полем confidence.

    Наследуемся от VacancyDetail, чтобы сохранить все поля детали вакансии
    и добавить к ним только оценку соответствия.
    """

    confidence: float = 0.0
    reason: str | None = None

    @classmethod
    def from_detail(
        cls, detail: VacancyDetail, confidence: float, reason: str | None = None
    ) -> "FilteredVacancyDetail":
        """Удобный конструктор поверх базовой VacancyDetail."""
        return cls(
            vacancy_id=detail.vacancy_id,
            name=detail.name,
            company_name=detail.company_name,
            area_name=detail.area_name,
            compensation=detail.compensation,
            publication_date=detail.publication_date,
            work_experience=detail.work_experience,
            employment=detail.employment,
            work_formats=list(detail.work_formats or []),
            schedule_by_days=list(detail.schedule_by_days or []),
            working_hours=list(detail.working_hours or []),
            link=detail.link,
            key_skills=list(detail.key_skills or []),
            description_html=detail.description_html,
            confidence=confidence,
            reason=reason,
        )


@dataclass(slots=True)
class FilteredVacancyDetailWithCoverLetter(FilteredVacancyDetail):
    """Детальная вакансия с опциональным сопроводительным письмом.

    Наследуется от FilteredVacancyDetail и добавляет поле для сопроводительного письма.
    """

    cover_letter: str | None = None

    @classmethod
    def from_filtered_detail(
        cls,
        filtered: FilteredVacancyDetail,
        cover_letter: str | None = None,
    ) -> "FilteredVacancyDetailWithCoverLetter":
        """Создает экземпляр из FilteredVacancyDetail с опциональным письмом.

        Args:
            filtered: Базовая вакансия с оценкой релевантности.
            cover_letter: Опциональное сопроводительное письмо.

        Returns:
            Экземпляр FilteredVacancyDetailWithCoverLetter со всеми полями из filtered и cover_letter.
        """
        return cls(
            vacancy_id=filtered.vacancy_id,
            name=filtered.name,
            company_name=filtered.company_name,
            area_name=filtered.area_name,
            compensation=filtered.compensation,
            publication_date=filtered.publication_date,
            work_experience=filtered.work_experience,
            employment=filtered.employment,
            work_formats=list(filtered.work_formats or []),
            schedule_by_days=list(filtered.schedule_by_days or []),
            working_hours=list(filtered.working_hours or []),
            link=filtered.link,
            key_skills=list(filtered.key_skills or []),
            description_html=filtered.description_html,
            confidence=filtered.confidence,
            reason=filtered.reason,
            cover_letter=cover_letter,
        )
