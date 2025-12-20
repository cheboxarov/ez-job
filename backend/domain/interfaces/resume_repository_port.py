"""Интерфейс репозитория резюме."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.resume import Resume


class ResumeRepositoryPort(ABC):
    """Порт репозитория резюме.

    Инфраструктура должна реализовать этот интерфейс.
    """

    @abstractmethod
    async def create(self, resume: Resume) -> Resume:
        """Создать резюме.

        Args:
            resume: Доменная сущность Resume для создания.

        Returns:
            Созданная доменная сущность Resume с заполненным id.
        """

    @abstractmethod
    async def update(self, resume: Resume) -> Resume:
        """Обновить резюме.

        Args:
            resume: Доменная сущность Resume с обновленными данными.

        Returns:
            Обновленная доменная сущность Resume.

        Raises:
            ValueError: Если резюме с таким ID не найдено.
        """

    @abstractmethod
    async def delete(self, resume_id: UUID) -> None:
        """Удалить резюме.

        Args:
            resume_id: UUID резюме для удаления.

        Raises:
            ValueError: Если резюме с таким ID не найдено.
        """

    @abstractmethod
    async def get_by_id(self, resume_id: UUID) -> Resume | None:
        """Получить резюме по ID.

        Args:
            resume_id: UUID резюме.

        Returns:
            Доменная сущность Resume или None, если резюме не найдено.
        """

    @abstractmethod
    async def list_by_user_id(self, user_id: UUID) -> list[Resume]:
        """Получить список резюме по ID пользователя.

        Args:
            user_id: UUID пользователя.

        Returns:
            Список доменных сущностей Resume.
        """

    @abstractmethod
    async def belongs_to_user(self, resume_id: UUID, user_id: UUID) -> bool:
        """Проверить, принадлежит ли резюме пользователю.

        Args:
            resume_id: UUID резюме.
            user_id: UUID пользователя.

        Returns:
            True, если резюме принадлежит пользователю, иначе False.
        """

    @abstractmethod
    async def get_by_external_id(
        self, external_id: str, user_id: UUID
    ) -> Resume | None:
        """Получить резюме по external_id и user_id.

        Args:
            external_id: Внешний ID резюме (например, ID из HH).
            user_id: UUID пользователя.

        Returns:
            Доменная сущность Resume или None, если резюме не найдено.
        """

    @abstractmethod
    async def get_all_active_auto_reply_resumes(self) -> list[Resume]:
        """Получить все резюме с включенным автооткликом.

        Returns:
            Список доменных сущностей Resume с is_auto_reply = True.
        """

    @abstractmethod
    async def get_by_headhunter_hash(
        self, user_id: UUID, headhunter_hash: str
    ) -> Resume | None:
        """Получить резюме по headhunter_hash и user_id.

        Args:
            user_id: UUID пользователя.
            headhunter_hash: Hash резюме в HeadHunter.

        Returns:
            Доменная сущность Resume или None, если резюме не найдено.
        """
