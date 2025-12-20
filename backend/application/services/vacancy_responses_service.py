"""Сервис для работы с откликами на вакансии."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from domain.entities.vacancy_response import VacancyResponse
from domain.use_cases.get_vacancy_responses_by_resume import (
    GetVacancyResponsesByResumeUseCase,
)


@dataclass
class VacancyResponsesListResult:
    """Результат получения списка откликов с метаинформацией пагинации."""

    items: list[VacancyResponse]
    total: int
    offset: int
    limit: int


class VacancyResponsesService:
    """Сервис для получения откликов на вакансии."""

    def __init__(
        self,
        get_vacancy_responses_by_resume_uc: GetVacancyResponsesByResumeUseCase,
    ) -> None:
        """Инициализация сервиса.

        Args:
            get_vacancy_responses_by_resume_uc: Use case для получения откликов по резюме.
        """
        self._get_vacancy_responses_by_resume_uc = get_vacancy_responses_by_resume_uc

    async def get_responses_by_resume_hash(
        self,
        *,
        user_id: UUID,
        resume_hash: str,
        offset: int = 0,
        limit: int = 50,
    ) -> VacancyResponsesListResult:
        """Получить отклики на вакансии по hash резюме.

        Args:
            user_id: UUID пользователя.
            resume_hash: Hash резюме в HeadHunter (headhunter_hash).
            offset: Смещение для пагинации (по умолчанию 0).
            limit: Количество записей для возврата (по умолчанию 50).

        Returns:
            Результат с данными и метаинформацией пагинации.

        Raises:
            ValueError: Если резюме не найдено или не принадлежит пользователю,
                или параметры пагинации невалидны.
        """
        responses, total = await self._get_vacancy_responses_by_resume_uc.execute(
            user_id=user_id,
            resume_hash=resume_hash,
            offset=offset,
            limit=limit,
        )

        return VacancyResponsesListResult(
            items=responses,
            total=total,
            offset=offset,
            limit=limit,
        )
