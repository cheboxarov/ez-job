"""Сервис для редактирования резюме."""

from __future__ import annotations

from typing import Callable, TYPE_CHECKING
from uuid import UUID

from domain.entities.resume import Resume
from domain.entities.resume_edit_result import ResumeEditResult
from domain.interfaces.resume_editor_port import ResumeEditorPort
from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from domain.use_cases.generate_resume_edits import GenerateResumeEditsUseCase
from domain.use_cases.get_resume import GetResumeUseCase
from loguru import logger

if TYPE_CHECKING:
    from loguru import Logger


class ResumeEditService:
    """Сервис для редактирования резюме.

    Оркестрирует работу use case'ов для генерации правок резюме.
    """

    def __init__(
        self,
        unit_of_work: UnitOfWorkPort,
        resume_editor: ResumeEditorPort,
    ) -> None:
        """Инициализация сервиса.

        Args:
            unit_of_work: UnitOfWork для управления транзакциями.
            resume_editor: Агент для редактирования резюме.
        """
        self._unit_of_work = unit_of_work
        self._resume_editor = resume_editor

    async def get_resume_for_editing(
        self, resume_id: UUID, user_id: UUID
    ) -> Resume | None:
        """Получить резюме для редактирования.

        Args:
            resume_id: UUID резюме.
            user_id: UUID пользователя.

        Returns:
            Доменная сущность Resume или None, если не найдено.

        Raises:
            PermissionError: Если резюме не принадлежит пользователю.
        """
        async with self._unit_of_work:
            use_case = GetResumeUseCase(self._unit_of_work.resume_repository)
            return await use_case.execute(resume_id=resume_id, user_id=user_id)

    async def generate_edits(
        self,
        resume_id: UUID,
        user_id: UUID,
        user_message: str,
        resume_text: str | None = None,
        history: list[dict] | None = None,
        current_plan: list[dict] | None = None,
        current_task: dict | None = None,
        streaming_callback: Callable[[str], None] | None = None,
        session_logger: "Logger | None" = None,
    ) -> ResumeEditResult:
        """Сгенерировать правки для резюме.

        Args:
            resume_id: UUID резюме.
            user_id: UUID пользователя.
            user_message: Сообщение пользователя с запросом на изменение.
            resume_text: Текст резюме (если не передан, загружается из БД).
            history: История диалога (опционально).
            current_plan: Текущий план выполнения (опционально).
            streaming_callback: Callback для отправки стриминговых chunks (опционально).
            session_logger: Логгер для записи в файл сессии (опционально).

        Returns:
            ResumeEditResult с предложенными изменениями.

        Raises:
            ValueError: Если резюме не найдено или не принадлежит пользователю.
        """
        # Загружаем резюме, если текст не передан
        if resume_text is None:
            resume = await self.get_resume_for_editing(resume_id, user_id)
            if resume is None:
                raise ValueError(f"Резюме {resume_id} не найдено")
            resume_text = resume.content

        # Санитизация типов (иногда источники могут вернуть None/не-строку)
        if resume_text is not None and not isinstance(resume_text, str):
            resume_text = str(resume_text)

        if not resume_text:
            raise ValueError("Текст резюме пуст")

        logger.info(
            f"Генерация правок для резюме {resume_id} "
            f"(user_id: {user_id}, длина резюме: {len(resume_text)})"
        )

        # Используем use case для генерации правок
        use_case = GenerateResumeEditsUseCase(self._resume_editor)

        result = await use_case.execute(
            resume_text=resume_text,
            user_message=user_message,
            history=history,
            current_plan=current_plan,
            current_task=current_task,
            user_id=user_id,
            streaming_callback=streaming_callback,
            session_logger=session_logger,
        )

        logger.info(
            f"Генерация правок завершена для резюме {resume_id}: "
            f"{len(result.patches)} patch, {len(result.questions)} вопросов"
        )

        return result
