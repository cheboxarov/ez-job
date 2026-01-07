"""Интерфейс для генерации сопроводительных писем."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID


class CoverLetterGeneratorPort(ABC):
    """Порт для генерации сопроводительных писем.

    Инфраструктура должна реализовать этот интерфейс.
    """

    @abstractmethod
    async def generate(
        self,
        resume: str,
        vacancy_description: str,
        user_params: str | None = None,
        user_id: UUID | None = None,
    ) -> str:
        """Сгенерировать сопроводительное письмо для вакансии.

        Args:
            resume: Текст резюме кандидата.
            vacancy_description: Описание вакансии (название, требования, обязанности).
            user_params: Дополнительные требования/предпочтения пользователя (опционально).

        Returns:
            Текст сопроводительного письма.
        """
