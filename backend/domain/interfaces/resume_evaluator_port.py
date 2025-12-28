from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class ResumeEvaluatorPort(ABC):
    """Интерфейс для агента оценки резюме."""

    @abstractmethod
    async def evaluate(self, resume_content: str) -> Dict[str, Any]:
        """Оценить резюме на основе правил.

        Args:
            resume_content: Текст резюме.

        Returns:
            Dict с оценкой (conf: float) и замечаниями.
        """
        pass
