"""Интерфейс сервиса резюме."""

from __future__ import annotations

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict
from uuid import UUID

from domain.entities.resume import Resume
from domain.interfaces.hh_client_port import HHClientPort


class ResumeServicePort(ABC):
    """Порт сервиса резюме.

    Application слой должен реализовать этот интерфейс.
    Сервис оркестрирует use case'ы для работы с резюме.
    """

    @abstractmethod
    async def create_resume(
        self,
        user_id: UUID,
        content: str,
        user_parameters: str | None = None,
    ) -> Resume:
        """Создать резюме для пользователя.

        Args:
            user_id: UUID пользователя.
            content: Текст резюме.
            user_parameters: Дополнительные параметры фильтрации.

        Returns:
            Созданная доменная сущность Resume.
        """

    @abstractmethod
    async def get_resume(self, resume_id: UUID, user_id: UUID) -> Resume | None:
        """Получить резюме по ID.

        Проверяет принадлежность резюме пользователю перед возвратом.

        Args:
            resume_id: UUID резюме.
            user_id: UUID пользователя (для проверки принадлежности).

        Returns:
            Доменная сущность Resume или None, если не найдено.

        Raises:
            PermissionError: Если резюме не принадлежит пользователю.
        """

    @abstractmethod
    async def list_user_resumes(self, user_id: UUID) -> list[Resume]:
        """Получить список резюме пользователя.

        Args:
            user_id: UUID пользователя.

        Returns:
            Список доменных сущностей Resume.
        """

    @abstractmethod
    async def update_resume(
        self,
        resume_id: UUID,
        user_id: UUID,
        content: str | None = None,
        user_parameters: str | None = None,
    ) -> Resume:
        """Обновить резюме.

        Проверяет принадлежность резюме пользователю перед обновлением.

        Args:
            resume_id: UUID резюме.
            user_id: UUID пользователя (для проверки принадлежности).
            content: Новый текст резюме (опционально).
            user_parameters: Новые параметры фильтрации (опционально).

        Returns:
            Обновленная доменная сущность Resume.

        Raises:
            PermissionError: Если резюме не принадлежит пользователю.
            ValueError: Если резюме не найдено.
        """

    @abstractmethod
    async def delete_resume(self, resume_id: UUID, user_id: UUID) -> None:
        """Удалить резюме.

        Проверяет принадлежность резюме пользователю перед удалением.

        Args:
            resume_id: UUID резюме.
            user_id: UUID пользователя (для проверки принадлежности).

        Raises:
            PermissionError: Если резюме не принадлежит пользователю.
            ValueError: Если резюме не найдено.
        """

    @abstractmethod
    async def import_resume_from_hh(
        self,
        user_id: UUID,
        hh_client: HHClientPort,
        headers: Dict[str, str],
        cookies: Dict[str, str],
    ) -> list[Resume]:
        """Импортировать резюме из HeadHunter.

        Получает список резюме из HH, для каждого получает детальную информацию,
        формирует текстовый контент и создает резюме в БД.

        Args:
            user_id: UUID пользователя.
            hh_client: Клиент для работы с HeadHunter API.
            headers: Заголовки для запроса к HH API.
            cookies: Куки для запроса к HH API.

        Returns:
            Список созданных резюме в БД.
        """
