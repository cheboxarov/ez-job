from __future__ import annotations

from typing import Any, Dict
from uuid import UUID

from domain.interfaces.resume_evaluator_port import ResumeEvaluatorPort
from domain.exceptions.agent_exceptions import AgentParseError
from loguru import logger


class EvaluateResumeUseCase:
    """Use case для оценки резюме."""

    def __init__(self, resume_evaluator: ResumeEvaluatorPort) -> None:
        """Инициализация.

        Args:
            resume_evaluator: Агент для оценки резюме.
        """
        self._resume_evaluator = resume_evaluator

    async def execute(self, resume_content: str, user_id: UUID | None = None) -> Dict[str, Any]:
        """Оценить резюме.

        Args:
            resume_content: Текст резюме.

        Returns:
            Dict с оценкой и замечаниями.
        """
        try:
            return await self._resume_evaluator.evaluate(resume_content, user_id)
        except AgentParseError as exc:
            logger.error(
                f"Ошибка парсинга ответа агента при оценке резюме: {exc}",
                exc_info=True,
            )
            return {
                "conf": 0.0,
                "remarks": [
                    {
                        "rule": "System",
                        "comment": str(exc),
                        "improvement": "Попробуйте позже",
                    }
                ],
                "summary": "Произошла ошибка при анализе резюме",
            }
