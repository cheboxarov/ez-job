"""Обработчик WebSocket соединений для редактирования резюме."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger

from application.services.resume_edit_service import ResumeEditService
from domain.entities.resume_edit_result import ResumeEditResult
from infrastructure.agents.resume_edit.deepagents.state_mapper import (
    build_agent_input,
    get_current_task,
    state_to_resume_edit_result,
)
from infrastructure.agents.resume_edit.deepagents.streaming_adapter import (
    stream_deep_agent_to_websocket,
)


class ResumeEditWebSocketHandler:
    """Обработчик WebSocket соединений для редактирования резюме.

    Обрабатывает двустороннюю коммуникацию через WebSocket:
    - Принимает сообщения от клиента (user_message, answer_question, apply_patch)
    - Отправляет ответы через WebSocket (assistant_message, questions, patches, streaming, error)
    """

    def __init__(self, resume_edit_service: ResumeEditService, deep_agent) -> None:
        """Инициализация обработчика.

        Args:
            resume_edit_service: Сервис для редактирования резюме.
            deep_agent: DeepAgent (LangGraph) для генерации ответов.
        """
        self._resume_edit_service = resume_edit_service
        self._deep_agent = deep_agent
        self._chat_history: dict[UUID, list[dict]] = {}  # resume_id -> history
        self._chat_plan: dict[UUID, list[dict]] = {}  # resume_id -> current plan
        self._processing_flags: dict[UUID, bool] = {}  # resume_id -> is processing
        self._session_loggers: dict[UUID, logger] = {}  # resume_id -> session logger
        # Определяем путь к логам: в Docker это /app/logs, локально - logs
        import os
        workdir = os.getcwd()
        if workdir == "/app" or Path("/app/logs").exists():
            self._logs_dir = Path("/app/logs")
        else:
            self._logs_dir = Path("logs")
        self._logs_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Логи WebSocket сессий будут сохраняться в: {self._logs_dir.absolute()}")

    async def _generate_edits_with_retry(
        self,
        *,
        resume_id: UUID,
        user_id: UUID,
        user_message: str,
        resume_text: str | None,
        history: list[dict] | None,
        current_plan: list[dict] | None,
        current_task: dict | None,
        websocket: WebSocket,
        session_key: UUID,
        max_attempts: int = 2,
    ) -> ResumeEditResult:
        """Вызвать генерацию правок DeepAgent с ретраями для частых TypeError."""
        last_exc: Exception | None = None

        for attempt in range(1, max_attempts + 1):
            try:
                input_state = build_agent_input(
                    resume_text=resume_text or "",
                    user_message=user_message,
                    history=history,
                    current_plan=current_plan,
                    current_task=current_task,
                )
                final_state = await stream_deep_agent_to_websocket(
                    agent=self._deep_agent,
                    input_data=input_state,
                    websocket_send=lambda msg_type, data: self._send_message(
                        websocket, msg_type, data, session_key=session_key
                    ),
                    send_plan_updates=False,
                )
                return state_to_resume_edit_result(final_state)
            except TypeError as exc:
                last_exc = exc
                msg = str(exc)
                if "must be str, not NoneType" not in msg or attempt >= max_attempts:
                    raise

                # Пытаемся санитизировать входные данные и повторить
                logger.warning(
                    f"TypeError при генерации правок (attempt {attempt}/{max_attempts}): {msg}. Делаю retry."
                )

                # Если текст резюме не передан, подгружаем его один раз
                if resume_text is None:
                    try:
                        resume = await self._resume_edit_service.get_resume_for_editing(
                            resume_id, user_id
                        )
                        if resume:
                            resume_text = resume.content
                    except Exception:
                        pass

                if resume_text is not None and not isinstance(resume_text, str):
                    resume_text = str(resume_text)
                if not isinstance(user_message, str):
                    user_message = str(user_message)

                await asyncio.sleep(0.2 * attempt)

        if last_exc:
            raise last_exc
        raise RuntimeError("Не удалось сгенерировать правки: неизвестная ошибка")

    async def handle_connection(
        self, websocket: WebSocket, resume_id: UUID, user_id: UUID
    ) -> None:
        """Обработать WebSocket соединение для редактирования резюме.

        Args:
            websocket: WebSocket соединение.
            resume_id: UUID резюме.
            user_id: UUID пользователя.
        """
        await websocket.accept()
        logger.info(
            f"WebSocket соединение для редактирования резюме принято: "
            f"resume_id={resume_id}, user_id={user_id}"
        )

        # Инициализируем историю и план для этой сессии
        session_key = resume_id
        if session_key not in self._chat_history:
            self._chat_history[session_key] = []
        if session_key not in self._chat_plan:
            self._chat_plan[session_key] = []

        # Создаем логгер для сессии
        session_logger = self._create_session_logger(resume_id, user_id)
        self._session_loggers[session_key] = session_logger

        session_logger.info(
            f"=== WebSocket сессия начата ==="
            f"\nresume_id: {resume_id}"
            f"\nuser_id: {user_id}"
            f"\ntimestamp: {datetime.now().isoformat()}"
        )

        try:
            # Отправляем приветственное сообщение
            await self._send_message(
                websocket,
                "assistant_message",
                {
                    "message": "Привет! Я помогу вам отредактировать резюме. "
                    "Опишите, какие изменения вы хотите внести."
                },
                session_key=session_key,
            )

            # Основной цикл обработки сообщений
            while True:
                try:
                    # Получаем сообщение от клиента
                    data = await websocket.receive_json()
                    message_type = data.get("type")

                    # Логируем входящее сообщение
                    if session_key in self._session_loggers:
                        self._session_loggers[session_key].info(
                            f"=== ВХОДЯЩЕЕ СООБЩЕНИЕ ===\n"
                            f"type: {message_type}\n"
                            f"data: {json.dumps(data.get('data', {}), ensure_ascii=False, indent=2)}\n"
                            f"timestamp: {datetime.now().isoformat()}"
                        )

                    if message_type == "user_message":
                        await self._handle_user_message(
                            websocket, resume_id, user_id, data.get("data", {})
                        )
                    elif message_type == "answer_question":
                        await self._handle_answer_question(
                            websocket, resume_id, user_id, data.get("data", {})
                        )
                    elif message_type == "answer_all_questions":
                        await self._handle_answer_all_questions(
                            websocket, resume_id, user_id, data.get("data", {})
                        )
                    elif message_type == "apply_patch":
                        await self._handle_apply_patch(
                            websocket, resume_id, user_id, data.get("data", {})
                        )
                    else:
                        await self._send_error(
                            websocket, f"Неизвестный тип сообщения: {message_type}", session_key=session_key
                        )

                except WebSocketDisconnect:
                    logger.info(
                        f"WebSocket соединение закрыто клиентом: "
                        f"resume_id={resume_id}, user_id={user_id}"
                    )
                    break
                except json.JSONDecodeError as exc:
                    logger.error(f"Ошибка парсинга JSON: {exc}")
                    await self._send_error(websocket, "Неверный формат JSON", session_key=session_key)
                except Exception as exc:
                    logger.error(
                        f"Ошибка при обработке сообщения: {exc}",
                        exc_info=True,
                    )
                    await self._send_error(websocket, f"Ошибка: {str(exc)}", session_key=session_key)

        except Exception as exc:
            logger.error(
                f"Ошибка в обработке WebSocket соединения: {exc}",
                exc_info=True,
            )
        finally:
            # Логируем завершение сессии
            if session_key in self._session_loggers:
                session_logger = self._session_loggers[session_key]
                session_logger.info(
                    f"=== WebSocket сессия завершена ==="
                    f"\nresume_id: {resume_id}"
                    f"\nuser_id: {user_id}"
                    f"\ntimestamp: {datetime.now().isoformat()}"
                )
                
                # Удаляем handlers для этой сессии
                if hasattr(self, "_session_handler_ids") and session_key in self._session_handler_ids:
                    for handler_id in self._session_handler_ids[session_key]:
                        try:
                            logger.remove(handler_id)
                        except Exception:
                            pass
                    del self._session_handler_ids[session_key]
                
                # Удаляем логгер из словаря
                del self._session_loggers[session_key]

            if session_key in self._chat_history:
                del self._chat_history[session_key]
            if session_key in self._chat_plan:
                del self._chat_plan[session_key]
            logger.info(
                f"WebSocket соединение закрыто: resume_id={resume_id}, user_id={user_id}"
            )

    async def _handle_user_message(
        self, websocket: WebSocket, resume_id: UUID, user_id: UUID, data: dict
    ) -> None:
        """Обработать сообщение пользователя."""
        message = data.get("message", "")
        resume_text = data.get("resume_text")
        history = data.get("history")
        session_key = resume_id

        if history is None:
            history = self._chat_history.get(session_key, [])

        current_plan = self._chat_plan.get(session_key, [])
        current_task = get_current_task(current_plan)

        if not message:
            await self._send_error(
                websocket, "Сообщение не может быть пустым", session_key=session_key
            )
            return

        if resume_text is None:
            try:
                resume = await self._resume_edit_service.get_resume_for_editing(
                    resume_id, user_id
                )
                if resume:
                    resume_text = resume.content
            except Exception:
                resume_text = resume_text or ""
        if resume_text is not None and not isinstance(resume_text, str):
            resume_text = str(resume_text)
        if not resume_text:
            await self._send_error(
                websocket, "Резюме не найдено", session_key=session_key
            )
            return

        if session_key in self._session_loggers:
            self._session_loggers[session_key].info(
                f"=== НАЧАЛО ГЕНЕРАЦИИ ПРАВОК ===\n"
                f"user_message: {message}\n"
                f"resume_text_length: {len(resume_text) if resume_text else 0}\n"
                f"history_length: {len(history) if history else 0}\n"
                f"timestamp: {datetime.now().isoformat()}"
            )

        try:
            result = await self._generate_edits_with_retry(
                resume_id=resume_id,
                user_id=user_id,
                user_message=message,
                resume_text=resume_text,
                history=history,
                current_plan=current_plan,
                current_task=current_task,
                websocket=websocket,
                session_key=session_key,
            )

            current_plan = result.plan or current_plan
            self._chat_plan[session_key] = current_plan

            if session_key in self._session_loggers:
                self._session_loggers[session_key].info(
                    "=== РЕЗУЛЬТАТ ГЕНЕРАЦИИ ===\n"
                    f"assistant_message: {result.assistant_message}\n"
                    f"patches_count: {len(result.patches)}\n"
                    f"questions_count: {len(result.questions)}\n"
                    f"plan_tasks: {len(current_plan)}\n"
                    f"warnings_count: {len(result.warnings)}\n"
                    f"timestamp: {datetime.now().isoformat()}"
                )

            await self._send_result(websocket, result, session_key)
            history.append({"user": message, "assistant": result.assistant_message})
            self._chat_history[session_key] = history

        except Exception as exc:
            logger.error(f"Ошибка при генерации правок: {exc}", exc_info=True)
            await self._send_error(
                websocket,
                f"Ошибка при генерации правок: {str(exc)}",
                session_key=session_key,
            )

    async def _handle_answer_question(
        self, websocket: WebSocket, resume_id: UUID, user_id: UUID, data: dict
    ) -> None:
        """Обработать ответ на вопрос."""
        session_key = resume_id
        
        if self._processing_flags.get(session_key, False):
            logger.warning(f"Игнорирование сообщения answer_question для сессии {session_key}: обработка уже идет")
            return
            
        self._processing_flags[session_key] = True
        
        try:
            question_id = data.get("question_id")
            answer = data.get("answer", "")

            if not question_id or not answer:
                await self._send_error(websocket, "question_id и answer обязательны", session_key=session_key)
                return

            history = self._chat_history.get(session_key, [])
            current_plan = self._chat_plan.get(session_key, [])
            current_task = get_current_task(current_plan)
            
            resume_text = data.get("resume_text")
            if not resume_text:
                try:
                    resume = await self._resume_edit_service.get_resume_for_editing(resume_id, user_id)
                    if resume:
                        resume_text = resume.content
                    else:
                        await self._send_error(websocket, "Резюме не найдено", session_key=session_key)
                        return
                except Exception as e:
                    logger.error(f"Ошибка при загрузке резюме: {e}", exc_info=True)
                    await self._send_error(websocket, f"Ошибка при загрузке резюме: {str(e)}", session_key=session_key)
                    return
            if resume_text is not None and not isinstance(resume_text, str):
                resume_text = str(resume_text)

            user_message = f"Ответ на вопрос {question_id}: {answer}"
            history.append({"user": user_message})

            if session_key in self._session_loggers:
                self._session_loggers[session_key].info(
                    f"=== ОТВЕТ НА ВОПРОС ===\n"
                    f"question_id: {question_id}\n"
                    f"answer: {answer}\n"
                    f"timestamp: {datetime.now().isoformat()}"
                )

            if session_key in self._session_loggers:
                self._session_loggers[session_key].info(
                    f"=== ПРОДОЛЖЕНИЕ ГЕНЕРАЦИИ ПОСЛЕ ОТВЕТА НА ВОПРОС ===\n"
                    f"user_message: {user_message}\n"
                    f"resume_text_length: {len(resume_text) if resume_text else 0}\n"
                    f"history_length: {len(history)}\n"
                    f"timestamp: {datetime.now().isoformat()}"
                )

            try:
                result = await self._generate_edits_with_retry(
                    resume_id=resume_id,
                    user_id=user_id,
                    user_message=user_message,
                    resume_text=resume_text,
                    history=history,
                    current_plan=current_plan,
                    current_task=current_task,
                    websocket=websocket,
                    session_key=session_key,
                )

                current_plan = result.plan or current_plan
                self._chat_plan[session_key] = current_plan

                if session_key in self._session_loggers:
                    self._session_loggers[session_key].info(
                        "=== РЕЗУЛЬТАТ ПРОДОЛЖЕНИЯ ГЕНЕРАЦИИ ===\n"
                        f"assistant_message: {result.assistant_message}\n"
                        f"patches_count: {len(result.patches)}\n"
                        f"questions_count: {len(result.questions)}\n"
                        f"plan_tasks: {len(current_plan)}\n"
                        f"warnings_count: {len(result.warnings)}\n"
                        f"timestamp: {datetime.now().isoformat()}"
                    )

                await self._send_result(websocket, result, session_key)
                history.append({"assistant": result.assistant_message})
                self._chat_history[session_key] = history

            except Exception as exc:
                logger.error(
                    f"Ошибка при продолжении генерации правок: {exc}", exc_info=True
                )
                await self._send_error(
                    websocket,
                    f"Ошибка при генерации правок: {str(exc)}",
                    session_key=session_key,
                )
        finally:
            self._processing_flags[session_key] = False

    async def _handle_answer_all_questions(
        self, websocket: WebSocket, resume_id: UUID, user_id: UUID, data: dict
    ) -> None:
        """Обработать ответы на все вопросы."""
        session_key = resume_id
        
        if self._processing_flags.get(session_key, False):
            return
            
        self._processing_flags[session_key] = True
        
        try:
            answers = data.get("answers", [])
            if not answers:
                await self._send_error(websocket, "answers обязательны", session_key=session_key)
                return

            history = self._chat_history.get(session_key, [])
            current_plan = self._chat_plan.get(session_key, [])
            current_task = get_current_task(current_plan)
            
            resume_text = data.get("resume_text")
            if not resume_text:
                try:
                    resume = await self._resume_edit_service.get_resume_for_editing(resume_id, user_id)
                    if resume:
                        resume_text = resume.content
                    else:
                        await self._send_error(websocket, "Резюме не найдено", session_key=session_key)
                        return
                except Exception as exc:
                    logger.error(f"Ошибка при загрузке резюме: {exc}", exc_info=True)
                    await self._send_error(
                        websocket,
                        f"Ошибка при загрузке резюме: {str(exc)}",
                        session_key=session_key,
                    )
                    return
            if resume_text is not None and not isinstance(resume_text, str):
                resume_text = str(resume_text)

            answers_text = "\n".join([f"Вопрос {a.get('questionId', '')}: {a.get('answer', '')}" for a in answers])
            user_message = f"Ответы на вопросы:\n{answers_text}"
            
            history.append({"user": user_message})

            try:
                result = await self._generate_edits_with_retry(
                    resume_id=resume_id,
                    user_id=user_id,
                    user_message=user_message,
                    resume_text=resume_text,
                    history=history,
                    current_plan=current_plan,
                    current_task=current_task,
                    websocket=websocket,
                    session_key=session_key,
                )

                current_plan = result.plan or current_plan
                self._chat_plan[session_key] = current_plan
                await self._send_result(websocket, result, session_key)

                history.append({"assistant": result.assistant_message})
                self._chat_history[session_key] = history

            except Exception as exc:
                logger.error(
                    f"Ошибка при продолжении генерации правок: {exc}", exc_info=True
                )
                await self._send_error(
                    websocket,
                    f"Ошибка при генерации правок: {str(exc)}",
                    session_key=session_key,
                )

        finally:
            self._processing_flags[session_key] = False

    async def _handle_apply_patch(
        self, websocket: WebSocket, resume_id: UUID, user_id: UUID, data: dict
    ) -> None:
        """Обработать применение patch."""
        session_key = resume_id
        patch_id = data.get("patch_id")

        if not patch_id:
            await self._send_error(websocket, "patch_id обязателен", session_key=session_key)
            return

        if session_key in self._session_loggers:
            self._session_loggers[session_key].info(
                f"=== ПРИМЕНЕНИЕ PATCH ===\n"
                f"patch_id: {patch_id}\n"
                f"timestamp: {datetime.now().isoformat()}"
            )

        await self._send_message(
            websocket,
            "patch_applied",
            {"patch_id": patch_id, "message": "Patch применен успешно"},
            session_key=session_key,
        )

    async def _send_result(
        self, websocket: WebSocket, result: ResumeEditResult, session_key: UUID | None = None
    ) -> None:
        """Отправить результат генерации правок."""
        await self._send_message(
            websocket,
            "assistant_message",
            {"message": result.assistant_message},
            session_key=session_key,
        )

        if result.questions:
            await self._send_message(
                websocket,
                "questions",
                {
                    "questions": [
                        {
                            "id": str(q.id),
                            "text": q.text,
                            "required": q.required,
                            "suggested_answers": q.suggested_answers,
                            "allow_multiple": q.allow_multiple,
                        }
                        for q in result.questions
                    ]
                },
                session_key=session_key,
            )

        if result.patches:
            await self._send_message(
                websocket,
                "patches",
                {
                    "patches": [
                        {
                            "id": patch.id or "",
                            "type": patch.type,
                            "start_line": patch.start_line,
                            "end_line": patch.end_line,
                            "old_text": patch.old_text,
                            "new_text": patch.new_text,
                            "reason": patch.reason,
                        }
                        for patch in result.patches
                    ]
                },
                session_key=session_key,
            )

        if result.plan:
            await self._send_message(
                websocket,
                "plan",
                {"plan": result.plan},
                session_key=session_key,
            )

        if result.warnings:
            await self._send_message(
                websocket,
                "warnings",
                {"warnings": result.warnings},
                session_key=session_key,
            )

    async def _send_message(
        self, websocket: WebSocket, message_type: str, data: dict, session_key: UUID | None = None
    ) -> None:
        """Отправить сообщение через WebSocket."""
        message = {"type": message_type, "data": data}
        await websocket.send_json(message)

        if session_key and session_key in self._session_loggers:
            if message_type == "streaming":
                if data.get("is_complete"):
                    self._session_loggers[session_key].info(
                        f"=== ИСХОДЯЩЕЕ СООБЩЕНИЕ ===\n"
                        f"type: {message_type}\n"
                        f"data: {{'is_complete': true}}\n"
                        f"timestamp: {datetime.now().isoformat()}"
                    )
            else:
                self._session_loggers[session_key].info(
                    f"=== ИСХОДЯЩЕЕ СООБЩЕНИЕ ===\n"
                    f"type: {message_type}\n"
                    f"data: {json.dumps(data, ensure_ascii=False, indent=2)}\n"
                    f"timestamp: {datetime.now().isoformat()}"
                )

    async def _send_error(
        self, websocket: WebSocket, error_message: str, session_key: UUID | None = None
    ) -> None:
        """Отправить сообщение об ошибке."""
        if session_key and session_key in self._session_loggers:
            self._session_loggers[session_key].error(
                f"=== ОШИБКА ===\n"
                f"error_message: {error_message}\n"
                f"timestamp: {datetime.now().isoformat()}"
            )

        await self._send_message(websocket, "error", {"message": error_message}, session_key=session_key)

    def _create_session_logger(self, resume_id: UUID, user_id: UUID) -> logger:
        """Создать логгер для сессии WebSocket."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self._logs_dir / f"resume_edit_ws_{resume_id}_{user_id}_{timestamp}.log"
        
        session_log_id = f"ws_session_{resume_id}_{user_id}_{timestamp}"

        handler_id = logger.add(
            str(log_file),
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
            level="INFO",
            rotation=None,
            retention="30 days",
            enqueue=True,
            filter=lambda record: record.get("extra", {}).get("session_log_id") == session_log_id,
        )

        session_logger = logger.bind(session_log_id=session_log_id)
        
        logger.info(f"Создан логгер для сессии WebSocket: {log_file.absolute()}")

        if not hasattr(self, "_session_handler_ids"):
            self._session_handler_ids: dict[UUID, list[int]] = {}
        if resume_id not in self._session_handler_ids:
            self._session_handler_ids[resume_id] = []
        self._session_handler_ids[resume_id].append(handler_id)

        return session_logger
