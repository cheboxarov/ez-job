"""Use case для получения откликов на вакансии по резюме."""

from __future__ import annotations

from uuid import UUID

from loguru import logger

from domain.entities.vacancy_response import VacancyResponse
from domain.interfaces.resume_repository_port import ResumeRepositoryPort
from domain.interfaces.vacancy_response_repository_port import (
    VacancyResponseRepositoryPort,
)


class GetVacancyResponsesByResumeUseCase:
    """Use case для получения откликов на вакансии по резюме.

    Проверяет принадлежность резюме пользователю и возвращает отклики с пагинацией.
    """

    def __init__(
        self,
        resume_repository: ResumeRepositoryPort,
        vacancy_response_repository: VacancyResponseRepositoryPort,
    ) -> None:
        """Инициализация use case.

        Args:
            resume_repository: Репозиторий для работы с резюме.
            vacancy_response_repository: Репозиторий для работы с откликами.
        """
        self._resume_repository = resume_repository
        self._vacancy_response_repository = vacancy_response_repository

    async def execute(
        self,
        *,
        user_id: UUID,
        resume_hash: str,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[VacancyResponse], int]:
        """Получить отклики на вакансии по резюме.

        Args:
            user_id: UUID пользователя.
            resume_hash: Hash резюме в HeadHunter (headhunter_hash).
            offset: Смещение для пагинации (по умолчанию 0).
            limit: Количество записей для возврата (по умолчанию 50).

        Returns:
            Кортеж из списка откликов и общего количества откликов.

        Raises:
            ValueError: Если резюме не найдено или не принадлежит пользователю.
        """
        # Валидация параметров пагинации
        if offset < 0:
            raise ValueError("offset должен быть >= 0")
        if limit <= 0:
            raise ValueError("limit должен быть > 0")
        if limit > 100:
            raise ValueError("limit не должен превышать 100")

        # Проверяем принадлежность резюме пользователю
        logger.info(
            f"Поиск резюме по headhunter_hash={resume_hash} для user_id={user_id}"
        )
        resume = await self._resume_repository.get_by_headhunter_hash(
            user_id=user_id, headhunter_hash=resume_hash
        )

        if resume is None:
            logger.warning(
                f"Резюме с hash={resume_hash} не найдено или не принадлежит пользователю {user_id}"
            )
            raise ValueError(
                "Резюме не найдено или не принадлежит вам"
            )

        logger.info(
            f"Найдено резюме: id={resume.id}, headhunter_hash={resume.headhunter_hash}, user_id={resume.user_id}"
        )

        # Получаем отклики с пагинацией по resume_hash
        try:
            logger.info(
                f"Поиск откликов для resume_hash={resume_hash}, offset={offset}, limit={limit}"
            )
            responses, total = await self._vacancy_response_repository.get_by_resume_hash_with_pagination(
                resume_hash=resume_hash,
                offset=offset,
                limit=limit,
            )
            logger.info(
                f"Получено {len(responses)} откликов для резюме {resume.id} "
                f"(всего: {total}, offset: {offset}, limit: {limit})"
            )
            return responses, total
        except Exception as exc:
            logger.error(
                f"Ошибка при получении откликов для резюме {resume.id}: {exc}",
                exc_info=True,
            )
            raise
