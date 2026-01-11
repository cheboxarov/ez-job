"""Use case для генерации правок резюме."""

from __future__ import annotations

from typing import Callable, TYPE_CHECKING
from uuid import UUID

from domain.entities.resume_edit_result import ResumeEditResult
from domain.exceptions.agent_exceptions import AgentParseError
from domain.interfaces.resume_editor_port import ResumeEditorPort
from loguru import logger

if TYPE_CHECKING:
    from loguru import Logger


class GenerateResumeEditsUseCase:
    """Use case для генерации правок резюме."""

    MAX_MESSAGE_LENGTH = 2000
    MAX_HISTORY_LENGTH = 50

    def __init__(self, resume_editor: ResumeEditorPort) -> None:
        """Инициализация.

        Args:
            resume_editor: Агент для редактирования резюме.
        """
        self._resume_editor = resume_editor

    async def execute(
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
            user_id: ID пользователя для логирования (опционально).
            streaming_callback: Callback для отправки стриминговых chunks (опционально).
            session_logger: Логгер для записи в файл сессии (опционально).

        Returns:
            ResumeEditResult с предложенными изменениями.

        Raises:
            ValueError: Если входные данные невалидны.
        """
        # Валидация входных данных
        if not resume_text or not resume_text.strip():
            raise ValueError("Текст резюме не может быть пустым")

        if not user_message or not user_message.strip():
            raise ValueError("Сообщение пользователя не может быть пустым")

        if len(user_message) > self.MAX_MESSAGE_LENGTH:
            raise ValueError(
                f"Сообщение пользователя слишком длинное (максимум {self.MAX_MESSAGE_LENGTH} символов)"
            )

        if history and len(history) > self.MAX_HISTORY_LENGTH:
            logger.warning(
                f"История диалога слишком длинная ({len(history)} элементов), "
                f"обрезаем до {self.MAX_HISTORY_LENGTH}"
            )
            history = history[-self.MAX_HISTORY_LENGTH :]

        try:
            result = await self._resume_editor.generate_edits(
                resume_text=resume_text,
                user_message=user_message,
                history=history,
                current_plan=current_plan,
                current_task=current_task,
                user_id=user_id,
                streaming_callback=streaming_callback,
                session_logger=session_logger,
            )

            # Валидация результата
            self._validate_result(result, resume_text)

            return result

        except AgentParseError as exc:
            logger.error(
                f"Ошибка парсинга ответа агента при редактировании резюме: {exc}",
                exc_info=True,
            )
            # Возвращаем пустой результат с предупреждением
            return ResumeEditResult(
                assistant_message="Произошла ошибка при генерации правок. Попробуйте позже.",
                warnings=[f"Ошибка: {str(exc)}"],
            )

    def _validate_result(self, result: ResumeEditResult, resume_text: str) -> None:
        """Валидация результата генерации правок.

        Args:
            result: Результат генерации правок.
            resume_text: Исходный текст резюме.

        Raises:
            ValueError: Если результат невалиден.
        """
        if not result.assistant_message:
            raise ValueError("Результат должен содержать сообщение агента")

        # Проверка лимитов на patch
        total_lines = len(resume_text.splitlines())
        if total_lines == 0:
            return

        changed_lines = set()
        for patch in result.patches:
            if patch.start_line is not None and patch.end_line is not None:
                for line_num in range(patch.start_line, patch.end_line + 1):
                    changed_lines.add(line_num)

        changed_lines_percent = (len(changed_lines) / total_lines) * 100
        max_changed_lines_percent = 25.0

        if changed_lines_percent > max_changed_lines_percent:
            result.warnings.append(
                f"Внимание: изменено {changed_lines_percent:.1f}% строк резюме "
                f"(максимум {max_changed_lines_percent}%). "
                "Рекомендуется проверить изменения."
            )

        if len(result.patches) > 12:
            result.warnings.append(
                f"Внимание: сгенерировано {len(result.patches)} patch-операций "
                "(максимум 12). Рекомендуется разбить запрос на несколько."
            )
