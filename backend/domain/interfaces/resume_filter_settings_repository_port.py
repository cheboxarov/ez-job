"""Интерфейс репозитория настроек фильтров резюме."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.resume_filter_settings import ResumeFilterSettings


class ResumeFilterSettingsRepositoryPort(ABC):
    """Порт репозитория настроек фильтров резюме."""

    @abstractmethod
    async def get_by_resume_id(self, resume_id: UUID) -> ResumeFilterSettings | None:
        """Получить настройки фильтров по ID резюме.

        Args:
            resume_id: UUID резюме.

        Returns:
            Доменная сущность ResumeFilterSettings или None, если не найдено.
        """

    @abstractmethod
    async def upsert_for_resume(
        self,
        resume_id: UUID,
        settings: ResumeFilterSettings,
    ) -> ResumeFilterSettings:
        """Создать или обновить настройки фильтров для резюме.

        Args:
            resume_id: UUID резюме.
            settings: Доменная сущность ResumeFilterSettings.

        Returns:
            Сохраненная доменная сущность ResumeFilterSettings.
        """
