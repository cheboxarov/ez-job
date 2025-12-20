"""Интерфейс для генерации сопроводительных писем."""

from __future__ import annotations

from abc import ABC, abstractmethod


class CoverLetterGeneratorPort(ABC):
    """Порт для генерации сопроводительных писем.

    Инфраструктура должна реализовать этот интерфейс.
    """

    @abstractmethod
    async def generate(self, resume: str, vacancy_description: str) -> str:
        """Сгенерировать сопроводительное письмо для вакансии.

        Args:
            resume: Текст резюме кандидата.
            vacancy_description: Описание вакансии (название, требования, обязанности).

        Returns:
            Текст сопроводительного письма.
        """
