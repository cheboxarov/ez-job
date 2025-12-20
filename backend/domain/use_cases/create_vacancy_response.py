"""Use case для создания отклика на вакансию в БД."""

from __future__ import annotations

from loguru import logger

from domain.entities.vacancy_response import VacancyResponse
from domain.interfaces.vacancy_response_repository_port import (
    VacancyResponseRepositoryPort,
)


class CreateVacancyResponseUseCase:
    """Use case для создания отклика на вакансию в БД.

    Базовый use case для сохранения отклика в базе данных.
    """

    def __init__(self, vacancy_response_repository: VacancyResponseRepositoryPort) -> None:
        """Инициализация use case.

        Args:
            vacancy_response_repository: Репозиторий для работы с откликами.
        """
        self._vacancy_response_repository = vacancy_response_repository

    async def execute(self, vacancy_response: VacancyResponse) -> VacancyResponse:
        """Создать отклик на вакансию в БД.

        Args:
            vacancy_response: Доменная сущность VacancyResponse для создания.

        Returns:
            Созданная доменная сущность VacancyResponse с заполненным id.

        Raises:
            Exception: При ошибках сохранения в БД.
        """
        try:
            logger.info(
                f"Создание отклика: vacancy_id={vacancy_response.vacancy_id}, "
                f"resume_id={vacancy_response.resume_id}, resume_hash={vacancy_response.resume_hash}, "
                f"user_id={vacancy_response.user_id}"
            )
            result = await self._vacancy_response_repository.create(vacancy_response)
            logger.info(
                f"Успешно создан отклик vacancy_id={vacancy_response.vacancy_id}, "
                f"resume_id={vacancy_response.resume_id}, resume_hash={vacancy_response.resume_hash}, "
                f"user_id={vacancy_response.user_id}"
            )
            return result
        except Exception as exc:
            logger.error(
                f"Ошибка при создании отклика vacancy_id={vacancy_response.vacancy_id}, "
                f"resume_id={vacancy_response.resume_id}, user_id={vacancy_response.user_id}: {exc}",
                exc_info=True,
            )
            raise
