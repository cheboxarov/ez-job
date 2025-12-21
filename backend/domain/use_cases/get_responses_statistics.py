"""Use case для получения статистики откликов за период."""

from __future__ import annotations

from datetime import date, timedelta
from uuid import UUID

from loguru import logger

from domain.interfaces.vacancy_response_repository_port import (
    VacancyResponseRepositoryPort,
)


class GetResponsesStatisticsUseCase:
    """Use case для получения статистики откликов за период."""

    def __init__(
        self,
        vacancy_response_repository: VacancyResponseRepositoryPort,
    ) -> None:
        """Инициализация use case.

        Args:
            vacancy_response_repository: Репозиторий откликов на вакансии.
        """
        self._vacancy_response_repository = vacancy_response_repository

    async def execute(
        self, user_id: UUID, days: int = 7
    ) -> list[tuple[date, int]]:
        """Получить статистику откликов за последние N дней.

        Args:
            user_id: UUID пользователя.
            days: Количество дней для статистики (по умолчанию 7).

        Returns:
            Список кортежей (дата, количество откликов) для каждого дня.
        """
        logger.info(f"Получение статистики откликов для user_id={user_id}, days={days}")

        # Вычисляем даты начала и конца периода
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)

        logger.info(
            f"Период статистики: {start_date} - {end_date} "
            f"(включительно, {days} дней)"
        )

        # Получаем статистику из репозитория
        statistics = await self._vacancy_response_repository.get_responses_count_by_date_range(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )

        logger.info(
            f"Получена статистика: {len(statistics)} дней, "
            f"всего откликов: {sum(count for _, count in statistics)}"
        )

        return statistics
