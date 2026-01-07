from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.filtered_vacancy import FilteredVacancyDetail


class CoverLetterServicePort(ABC):
    """Порт сервиса генерации сопроводительного письма."""

    @abstractmethod
    async def generate(
        self,
        vacancy: FilteredVacancyDetail,
        resume: str,
        user_id: UUID | None = None,
    ) -> str:
        """Генерирует сопроводительное письмо для указанной вакансии.

        Args:
            vacancy: Детальная информация о вакансии с оценкой релевантности.
            resume: Текст резюме кандидата.

        Returns:
            Текст сопроводительного письма на русском языке.
            Возвращает пустую строку в случае ошибки.
        """
        raise NotImplementedError
