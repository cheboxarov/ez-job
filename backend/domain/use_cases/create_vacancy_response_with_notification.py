"""Use case для создания отклика на вакансию с уведомлением через WebSocket."""

from __future__ import annotations

from loguru import logger

from domain.entities.vacancy_response import VacancyResponse
from domain.interfaces.event_publisher_port import EventPublisherPort
from domain.use_cases.create_vacancy_response import CreateVacancyResponseUseCase


class CreateVacancyResponseWithNotificationUseCase:
    """Use case для создания VacancyResponse с уведомлением через WebSocket.
    
    Создаёт отклик на вакансию и публикует событие в Event Bus для отправки через WebSocket.
    """

    def __init__(
        self,
        create_vacancy_response_uc: CreateVacancyResponseUseCase,
        event_publisher: EventPublisherPort,
    ) -> None:
        """Инициализация use case.
        
        Args:
            create_vacancy_response_uc: Use case для создания отклика на вакансию.
            event_publisher: Publisher для публикации событий.
        """
        self._create_vacancy_response_uc = create_vacancy_response_uc
        self._event_publisher = event_publisher

    async def execute(self, vacancy_response: VacancyResponse) -> VacancyResponse:
        """Создать отклик на вакансию и опубликовать событие.
        
        Args:
            vacancy_response: Доменная сущность VacancyResponse для создания.
        
        Returns:
            Созданная доменная сущность VacancyResponse с заполненным id.
        
        Raises:
            Exception: При ошибках сохранения в БД или публикации события.
        """
        try:
            # 1. Создаём отклик через оригинальный use case
            created_response = await self._create_vacancy_response_uc.execute(vacancy_response)
            
            # 2. Публикуем событие (не блокируем создание, если публикация не удалась)
            try:
                await self._event_publisher.publish_vacancy_response_created(created_response)
                logger.debug(
                    f"Событие vacancy_response_created опубликовано для отклика {created_response.id}"
                )
            except Exception as exc:
                logger.error(
                    f"Ошибка при публикации события vacancy_response_created для отклика {created_response.id}: {exc}",
                    exc_info=True,
                )
                # Не прерываем выполнение, если публикация не удалась
            
            return created_response
        except Exception as exc:
            logger.error(
                f"Ошибка при создании отклика на вакансию с уведомлением: {exc}",
                exc_info=True,
            )
            raise
