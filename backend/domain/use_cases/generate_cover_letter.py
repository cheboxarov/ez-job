from __future__ import annotations
from uuid import UUID

from loguru import logger

from domain.entities.filtered_vacancy import FilteredVacancyDetail
from domain.interfaces.cover_letter_service_port import CoverLetterServicePort
from domain.exceptions.agent_exceptions import AgentParseError


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
        user_id: UUID | None = None,
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
            cover_letter = await self._service.generate(vacancy, resume, user_id)
            return cover_letter
        except AgentParseError as exc:
            logger.error(
                f"[usecase] Ошибка парсинга ответа агента при генерации письма: {exc}",
                exc_info=True,
            )
            return ""
        except Exception as exc:  # pragma: no cover - диагностический путь
            logger.error(f"[usecase] ошибка при генерации письма: {exc}", exc_info=True)
            return ""
