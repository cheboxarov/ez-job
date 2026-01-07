from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict
from uuid import UUID


class ResumeEvaluatorPort(ABC):
    """Интерфейс для агента оценки резюме."""

    @abstractmethod
    async def evaluate(self, resume_content: str, user_id: UUID | None = None) -> Dict[str, Any]:
        """Оценить резюме на основе правил.

        Args:
            resume_content: Текст резюме.

        Returns:
            Dict с оценкой (conf: float) и замечаниями.
        """
        pass
