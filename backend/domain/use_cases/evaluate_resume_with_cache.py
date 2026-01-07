"""Use case для оценки резюме с кешированием."""

from __future__ import annotations

from typing import Any, Dict
from uuid import UUID

from domain.use_cases.evaluate_resume import EvaluateResumeUseCase
from domain.use_cases.get_resume_evaluation_from_cache import (
    GetResumeEvaluationFromCacheUseCase,
)
from domain.use_cases.save_resume_evaluation import SaveResumeEvaluationUseCase
from domain.utils.resume_hash import calculate_resume_content_hash


class EvaluateResumeWithCacheUseCase:
    """Use case для оценки резюме с кешированием результатов.

    Использует кеш для избежания повторных вызовов LLM для одинакового содержимого резюме.
    """

    def __init__(
        self,
        get_evaluation_from_cache_uc: GetResumeEvaluationFromCacheUseCase,
        evaluate_resume_uc: EvaluateResumeUseCase,
        save_evaluation_uc: SaveResumeEvaluationUseCase,
    ) -> None:
        """Инициализация.

        Args:
            get_evaluation_from_cache_uc: Use case для получения оценки из кеша.
            evaluate_resume_uc: Use case для оценки резюме через LLM.
            save_evaluation_uc: Use case для сохранения оценки в БД.
        """
        self._get_evaluation_from_cache_uc = get_evaluation_from_cache_uc
        self._evaluate_resume_uc = evaluate_resume_uc
        self._save_evaluation_uc = save_evaluation_uc

    async def execute(
        self, resume_content: str, user_id: UUID | None = None
    ) -> Dict[str, Any]:
        """Оценить резюме с использованием кеша.

        Сначала проверяет кеш по хешу содержимого резюме.
        Если оценка найдена в кеше, возвращает её.
        Если не найдена, запрашивает оценку у LLM, сохраняет в кеш и возвращает результат.

        Args:
            resume_content: Текст резюме.
            user_id: ID пользователя (опционально, для логирования вызовов LLM).

        Returns:
            Dict с оценкой (conf, remarks, summary).
        """
        # Вычисляем хеш содержимого резюме
        resume_content_hash = calculate_resume_content_hash(resume_content)

        # Пытаемся получить оценку из кеша
        cached_evaluation = await self._get_evaluation_from_cache_uc.execute(
            resume_content_hash
        )

        if cached_evaluation is not None:
            return cached_evaluation

        # Если не найдено в кеше, запрашиваем у LLM
        evaluation_data = await self._evaluate_resume_uc.execute(resume_content, user_id)

        # Сохраняем результат в кеш
        try:
            await self._save_evaluation_uc.execute(resume_content_hash, evaluation_data)
        except Exception as e:
            raise

        return evaluation_data
