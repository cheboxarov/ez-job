"""Интерфейс репозитория мэтчей резюме-вакансия."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List
from uuid import UUID

from domain.entities.resume_to_vacancy_match import ResumeToVacancyMatch


class ResumeToVacancyMatchRepositoryPort(ABC):
    """Порт репозитория мэтчей резюме-вакансия.

    Инфраструктура должна реализовать этот интерфейс.
    """

    @abstractmethod
    async def get_by_resume_and_vacancy_hash(
        self, resume_id: UUID, vacancy_hash: str
    ) -> ResumeToVacancyMatch | None:
        """Получить мэтч по resume_id и vacancy_hash.

        Args:
            resume_id: UUID резюме.
            vacancy_hash: Hash вакансии.

        Returns:
            Доменная сущность ResumeToVacancyMatch или None, если мэтч не найден.
        """

    @abstractmethod
    async def get_batch_by_resume_and_vacancy_hashes(
        self, resume_id: UUID, vacancy_hashes: List[str]
    ) -> Dict[str, ResumeToVacancyMatch]:
        """Батчевое получение мэтчей по resume_id и списку vacancy_hash.

        Args:
            resume_id: UUID резюме.
            vacancy_hashes: Список hash вакансий.

        Returns:
            Словарь vacancy_hash -> ResumeToVacancyMatch для найденных мэтчей.
        """

    @abstractmethod
    async def create(self, match: ResumeToVacancyMatch) -> ResumeToVacancyMatch:
        """Создать новый мэтч.

        Args:
            match: Доменная сущность ResumeToVacancyMatch для создания.

        Returns:
            Созданная доменная сущность ResumeToVacancyMatch.
        """

    @abstractmethod
    async def create_batch(
        self, matches: List[ResumeToVacancyMatch]
    ) -> List[ResumeToVacancyMatch]:
        """Батчевое создание мэтчей.

        Args:
            matches: Список доменных сущностей ResumeToVacancyMatch для создания.

        Returns:
            Список созданных доменных сущностей ResumeToVacancyMatch.
        """
