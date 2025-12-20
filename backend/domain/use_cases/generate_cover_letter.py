from __future__ import annotations

from domain.entities.filtered_vacancy import FilteredVacancyDetail
from domain.interfaces.cover_letter_service_port import CoverLetterServicePort


class GenerateCoverLetterUseCase:
    """Use case для генерации сопроводительного письма к вакансии.

    Инкапсулирует бизнес-логику генерации письма через сервис.
    """

    def __init__(
        self,
        cover_letter_service: CoverLetterServicePort,
    ) -> None:
        self._service = cover_letter_service

    async def execute(
        self,
        vacancy: FilteredVacancyDetail,
        resume: str,
    ) -> str:
        """Генерирует сопроводительное письмо для указанной вакансии.

        Args:
            vacancy: Детальная информация о вакансии с оценкой релевантности.
            resume: Текст резюме кандидата.

        Returns:
            Текст сопроводительного письма. Возвращает пустую строку в случае ошибки.
        """
        if not vacancy or not resume:
            return ""

        try:
            cover_letter = await self._service.generate(vacancy, resume)
            return cover_letter
        except Exception as exc:  # pragma: no cover - диагностический путь
            print(f"[usecase] ошибка при генерации письма: {exc}", flush=True)
            return ""
