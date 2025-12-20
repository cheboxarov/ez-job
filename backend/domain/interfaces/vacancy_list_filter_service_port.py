from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from domain.entities.filtered_vacancy_list import FilteredVacancyListDto
from domain.entities.vacancy_list import VacancyListItem


class VacancyListFilterServicePort(ABC):
    """Порт сервиса нейронной фильтрации list-вакансий."""

    @abstractmethod
    async def filter_vacancy_list(
        self,
        vacancies: List[VacancyListItem],
        resume: str,
        user_filter_params: str | None = None,
    ) -> List[FilteredVacancyListDto]:
        """Оценить релевантность списка list-вакансий к резюме.

        Предполагается, что в одном вызове передаётся не более ~50 вакансий,
        чтобы не раздувать контекст модели.

        Args:
            vacancies: Список list-вакансий для оценки.
            resume: Текст резюме кандидата.
            user_filter_params: Дополнительные требования пользователя к фильтрации
                (например, "нужна исключительно удаленка без гибрида").
                Если передан, учитывается при оценке вакансий.
        """
        raise NotImplementedError

