from __future__ import annotations

from typing import Any, Dict
from domain.interfaces.resume_evaluator_port import ResumeEvaluatorPort


class EvaluateResumeUseCase:
    """Use case для оценки резюме."""

    def __init__(self, resume_evaluator: ResumeEvaluatorPort) -> None:
        """Инициализация.

        Args:
            resume_evaluator: Агент для оценки резюме.
        """
        self._resume_evaluator = resume_evaluator

    async def execute(self, resume_content: str) -> Dict[str, Any]:
        """Оценить резюме.

        Args:
            resume_content: Текст резюме.

        Returns:
            Dict с оценкой и замечаниями.
        """
        return await self._resume_evaluator.evaluate(resume_content)
