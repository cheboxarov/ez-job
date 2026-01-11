"""Интерфейс для агента редактирования резюме."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, TYPE_CHECKING
from uuid import UUID

from domain.entities.resume_edit_result import ResumeEditResult

if TYPE_CHECKING:
    from loguru import Logger


class ResumeEditorPort(ABC):
    """Интерфейс для агента редактирования резюме."""

    @abstractmethod
    async def generate_edits(
        self,
        resume_text: str,
        user_message: str,
        history: list[dict] | None = None,
        current_plan: list[dict] | None = None,
        current_task: dict | None = None,
        user_id: UUID | None = None,
        streaming_callback: Callable[[str], None] | None = None,
        session_logger: "Logger | None" = None,
    ) -> ResumeEditResult:
        """Сгенерировать правки для резюме.

        Args:
            resume_text: Текст резюме для редактирования.
            user_message: Сообщение пользователя с запросом на изменение.
            history: История диалога (опционально).
            current_plan: Текущий план выполнения (опционально).
            current_task: Текущая активная задача плана (опционально).
            user_id: ID пользователя для логирования (опционально).
            streaming_callback: Callback для отправки стриминговых chunks (опционально).
            session_logger: Логгер для записи в файл сессии (опционально).

        Returns:
            ResumeEditResult с предложенными изменениями, вопросами и предупреждениями.
        """
        pass
