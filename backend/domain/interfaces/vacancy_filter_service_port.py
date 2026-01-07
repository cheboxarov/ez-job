from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from domain.entities.vacancy_detail import VacancyDetail
from domain.entities.filtered_vacancy import FilteredVacancyDto


class VacancyFilterServicePort(ABC):
    """Порт сервиса нейронной фильтрации вакансий."""

    @abstractmethod
    async def filter_vacancies(
        self,
        vacancies: List[VacancyDetail],
        resume: str,
        user_filter_params: str | None = None,
        user_id: UUID | None = None,
    ) -> List[FilteredVacancyDto]:
        """Оценить релевантность списка вакансий к резюме.

        Предполагается, что в одном вызове передаётся не более ~10 вакансий,
        чтобы не раздувать контекст модели.

        Args:
            vacancies: Список вакансий для оценки.
            resume: Текст резюме кандидата.
            user_filter_params: Дополнительные требования пользователя к фильтрации
                (например, "нужна исключительно удаленка без гибрида").
                Если передан, учитывается при оценке вакансий.
            user_id: ID пользователя для логирования (опционально).
        """
        raise NotImplementedError
