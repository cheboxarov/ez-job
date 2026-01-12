"""Мапперы состояния между DeepAgents и форматом сервиса редактирования резюме."""

from __future__ import annotations

import json
from typing import Any
from uuid import UUID, uuid4

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from loguru import logger

from domain.entities.resume_edit_patch import ResumeEditPatch
from domain.entities.resume_edit_question import ResumeEditQuestion
from domain.entities.resume_edit_result import ResumeEditResult
from domain.entities.llm_call import LlmCall
from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from datetime import datetime


_STATUS_VALUES = {"pending", "in_progress", "completed"}


def history_to_messages(history: list[dict] | None) -> list[BaseMessage]:
    """Преобразовать историю диалога в сообщения LangChain."""
    messages: list[BaseMessage] = []
    if not history:
        return messages
    for item in history:
        if not isinstance(item, dict):
            continue
        if item.get("user"):
            messages.append(HumanMessage(content=str(item.get("user"))))
        if item.get("assistant"):
            messages.append(AIMessage(content=str(item.get("assistant"))))
    return messages


def get_current_task(plan: list[dict] | None) -> dict | None:
    """Вернуть текущую задачу (in_progress) из плана."""
    for task in plan or []:
        if isinstance(task, dict) and task.get("status") == "in_progress":
            return task
    return None


def plan_to_todos(plan: list[dict] | None) -> list[dict]:
    """Преобразовать план в формат todos для DeepAgents."""
    todos: list[dict] = []
    for idx, task in enumerate(plan or [], start=1):
        if not isinstance(task, dict):
            continue
        status = task.get("status")
        if status not in _STATUS_VALUES:
            status = "pending"
        title = task.get("title") or task.get("content") or f"Шаг {idx}"
        todo: dict[str, Any] = {"content": str(title), "status": status}
        if task.get("id"):
            todo["id"] = str(task.get("id"))
        if task.get("agent_type"):
            todo["agent_type"] = str(task.get("agent_type"))
        description = task.get("description") or task.get("activeForm")
        if description:
            todo["description"] = str(description)
        active_form = task.get("activeForm") or task.get("active_form")
        if active_form:
            todo["activeForm"] = str(active_form)
        todos.append(todo)
    return todos


def todos_to_plan(todos: list[dict] | None) -> list[dict]:
    """Преобразовать todos в формат плана для фронтенда."""
    plan: list[dict] = []
    for idx, todo in enumerate(todos or [], start=1):
        if not isinstance(todo, dict):
            continue
        status = todo.get("status")
        if status not in _STATUS_VALUES:
            status = "pending"
        title = todo.get("content") or todo.get("title") or f"Шаг {idx}"
        task_id = todo.get("id") or f"todo-{idx}"
        description = todo.get("description") or todo.get("activeForm")
        task: dict[str, Any] = {
            "id": str(task_id),
            "title": str(title),
            "status": status,
        }
        if description:
            task["description"] = str(description)
        if todo.get("agent_type"):
            task["agent_type"] = todo.get("agent_type")
        plan.append(task)
    return plan


def build_user_prompt(
    resume_text: str,
    user_message: str,
    current_plan: list[dict] | None,
    current_task: dict | None,
    history: list[dict] | None,
    user_id: UUID | None = None,
) -> str:
    """Сформировать контекстный промпт для DeepAgent."""
    plan_block = json.dumps(current_plan or [], ensure_ascii=False, indent=2)
    task_block = json.dumps(current_task or {}, ensure_ascii=False, indent=2)
    history_block = json.dumps(history or [], ensure_ascii=False, indent=2)
    logger.info(f"history: {history}")
    last_assistant_message = ""
    for item in reversed(history or []):
        if isinstance(item, dict) and item.get("assistant"):
            last_assistant_message = str(item.get("assistant"))
            break
    last_assistant_block = last_assistant_message or "Нет"
    return (
        "КОНТЕКСТ РЕДАКТИРОВАНИЯ РЕЗЮМЕ\n\n"
        "ТЕКСТ РЕЗЮМЕ:\n"
        f"{resume_text}\n\n"
        "ТЕКУЩИЙ ПЛАН:\n"
        f"{plan_block}\n\n"
        "ТЕКУЩАЯ ЗАДАЧА:\n"
        f"{task_block}\n\n"
        "ПОСЛЕДНИЙ ОТВЕТ АССИСТЕНТА:\n"
        f"{last_assistant_block}\n\n"
        "ИСТОРИЯ ДИАЛОГА:\n"
        f"{history_block}\n\n"
        "СООБЩЕНИЕ ПОЛЬЗОВАТЕЛЯ:\n"
        f"{user_message}"
    )


def build_agent_input(
    resume_text: str | None,
    user_message: str,
    history: list[dict] | None,
    current_plan: list[dict] | None,
    current_task: dict | None,
    user_id: UUID | None = None,
) -> dict:
    """Сформировать входное состояние для DeepAgent."""
    normalized_resume_text = resume_text or ""
    messages = history_to_messages(history)
    messages.append(
        HumanMessage(
            content=build_user_prompt(
                normalized_resume_text,
                user_message,
                current_plan,
                current_task,
                history,
                user_id,
            )
        )
    )
    return {
        "messages": messages,
        "todos": plan_to_todos(current_plan),
        "resume_text": normalized_resume_text,
        "current_plan": current_plan or [],
        "current_task": current_task,
        "history": history or [],
        "user_id": str(user_id) if user_id else None,
    }


def _messages_to_last_ai_content(messages: list[BaseMessage]) -> str:
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content:
            return str(msg.content)
    return ""


def _parse_structured_response(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    return None


def _normalize_questions(raw_questions: list[dict]) -> list[ResumeEditQuestion]:
    questions: list[ResumeEditQuestion] = []
    for q_data in raw_questions or []:
        q_text = str(q_data.get("text", "")).strip()
        if not q_text:
            continue
        q_id = q_data.get("id") or str(uuid4())
        try:
            q_uuid = UUID(str(q_id))
        except ValueError:
            q_uuid = uuid4()
        questions.append(
            ResumeEditQuestion(
                id=q_uuid,
                text=q_text,
                required=bool(q_data.get("required", True)),
                suggested_answers=q_data.get("suggested_answers", []) or [],
                allow_multiple=bool(q_data.get("allow_multiple", False)),
            )
        )
    return questions


def _normalize_patches(raw_patches: list[dict]) -> list[ResumeEditPatch]:
    patches: list[ResumeEditPatch] = []
    for patch_data in raw_patches or []:
        patch_id = patch_data.get("id") or str(uuid4())
        try:
            patch = ResumeEditPatch(
                id=str(patch_id),
                type=patch_data.get("type", "replace"),  # type: ignore
                old_text=patch_data.get("old_text", ""),
                new_text=patch_data.get("new_text"),
                reason=patch_data.get("reason", ""),
                start_line=patch_data.get("start_line"),
                end_line=patch_data.get("end_line"),
            )
            patches.append(patch)
        except Exception as exc:
            logger.warning(
                f"Не удалось распарсить patch (пропускаем): patch_data={patch_data}, error={exc}"
            )
            continue
    return patches


async def _log_state_processing(
    state: dict,
    structured: dict[str, Any] | None,
    final_result: ResumeEditResult,
    unit_of_work: UnitOfWorkPort | None,
    user_id: UUID | None = None,
) -> None:
    """Логировать обработку состояния агента в LLM calls.
    
    Args:
        state: Состояние агента.
        structured: Распарсенный structured_response.
        final_result: Финальный результат обработки.
        unit_of_work: UnitOfWork для логирования.
        user_id: ID пользователя (опционально).
    """
    if not unit_of_work:
        return
    # Проверка типа state
    if not isinstance(state, dict):
        logger.warning(
            f"[_log_state_processing] state не является словарем: "
            f"type={type(state)}, value={str(state)[:500]}"
        )
        return
    

    
    try:
        import json
        
        # Собираем диагностическую информацию
        messages = state.get("messages", [])
        last_ai_messages = []
        tool_calls_info = []
        for msg in reversed(messages[-10:]):  # Последние 10 сообщений
            if isinstance(msg, AIMessage):
                content = str(msg.content) if msg.content else ""
                last_ai_messages.append({
                    "content": content[:500],
                    "content_length": len(content) if content else 0,
                    "has_tool_calls": hasattr(msg, "tool_calls") and bool(msg.tool_calls),
                })
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    tool_calls_info.append([{"name": tc.get("name"), "args": str(tc.get("args", {}))[:200]} for tc in msg.tool_calls])
        
        diagnostics = {
            "state_keys": list(state.keys()),
            "structured_response_type": str(type(state.get("structured_response"))),
            "structured_response_raw": str(state.get("structured_response"))[:2000] if state.get("structured_response") else None,
            "structured_response_parsed": json.dumps(structured, ensure_ascii=False, default=str)[:2000] if structured else None,
            "messages_count": len(messages),
            "last_ai_messages": last_ai_messages,
            "tool_calls": tool_calls_info,
            "last_ai_message": _messages_to_last_ai_content(messages)[:1000],
            "final_result": {
                "assistant_message": final_result.assistant_message[:500] if final_result.assistant_message else None,
                "questions_count": len(final_result.questions),
                "patches_count": len(final_result.patches),
                "warnings_count": len(final_result.warnings),
            }
        }
        
        # Форматируем как текст для response
        response_text = "=== ДИАГНОСТИКА ОБРАБОТКИ СОСТОЯНИЯ ===\n"
        response_text += json.dumps(diagnostics, ensure_ascii=False, indent=2, default=str)
        
        # Создаем запись в LLM calls
        llm_call = LlmCall(
            id=uuid4(),
            call_id=uuid4(),
            attempt_number=1,
            agent_name="ResumeEditDeepAgentStateProcessor",
            model="state_processor",
            user_id=user_id,
            prompt=[{"role": "system", "content": "State processing diagnostic"}],
            response=response_text,
            temperature=0.0,
            response_format=None,
            status="success",
            error_type=None,
            error_message=None,
            duration_ms=None,
            prompt_tokens=None,
            completion_tokens=None,
            total_tokens=None,
            response_size_bytes=len(response_text.encode("utf-8")) if response_text else None,
            cost_usd=None,
            context={"use_case": "resume_edit_deep_agent_state_processing"},
            created_at=datetime.now(),
        )
        
        await unit_of_work.standalone_llm_call_repository.create(llm_call)
    except Exception as exc:
        logger.error(
            f"[_log_state_processing] Ошибка при логировании обработки состояния: {exc}",
            exc_info=True,
        )


async def state_to_resume_edit_result(
    state: dict,
    unit_of_work: UnitOfWorkPort | None = None,
    user_id: UUID | None = None,
) -> ResumeEditResult:
    """Преобразовать состояние DeepAgent в ResumeEditResult.
    
    Args:
        state: Состояние DeepAgent.
        unit_of_work: UnitOfWork для логирования (опционально).
        user_id: ID пользователя для логирования (опционально).
    
    Returns:
        ResumeEditResult с результатом обработки.
    """
    # Проверка типа state
    if not isinstance(state, dict):
        logger.warning(
            f"[state_to_resume_edit_result] state не является словарем: "
            f"type={type(state)}, value={str(state)[:500]}"
        )
        if state is None:
            state = {}
        else:
            # Преобразуем в пустой словарь и возвращаем fallback результат
            return ResumeEditResult(
                assistant_message="Произошла ошибка при обработке состояния агента.",
                plan=[],
            )
    

    structured = _parse_structured_response(state.get("structured_response"))
    messages = state.get("messages", [])
    
    # Детальное логирование для диагностики
    logger.info(
        f"[state_to_resume_edit_result] structured_response type: {type(state.get('structured_response'))}, "
        f"value: {str(state.get('structured_response'))[:500] if state.get('structured_response') else None}"
    )
    logger.info(
        f"[state_to_resume_edit_result] structured parsed: {structured is not None}, "
        f"messages count: {len(messages)}"
    )

    if structured is None:
        fallback = _messages_to_last_ai_content(messages)
        logger.info(
            f"[state_to_resume_edit_result] structured is None, fallback message: {fallback[:200] if fallback else 'EMPTY'}"
        )
        try:
            structured = json.loads(fallback) if fallback else None
        except json.JSONDecodeError:
            structured = None
            logger.warning(
                f"[state_to_resume_edit_result] Failed to parse fallback as JSON: {fallback[:200] if fallback else 'EMPTY'}"
            )

    if not structured:
        assistant_message = _messages_to_last_ai_content(messages)
        logger.warning(
            f"[state_to_resume_edit_result] No structured response found. "
            f"Last AI message: {assistant_message[:200] if assistant_message else 'EMPTY'}. "
            f"Using fallback message."
        )
        # Если последнее сообщение пустое, но есть инструменты, пытаемся понять контекст
        if not assistant_message:
            # Проверяем, были ли вызовы инструментов
            tool_calls = []
            for msg in reversed(messages):
                if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
                    tool_calls = msg.tool_calls
                    break
            if tool_calls:
                assistant_message = f"Обрабатываю запрос. Вызвано инструментов: {len(tool_calls)}."
                logger.info(
                    f"[state_to_resume_edit_result] Found tool calls but empty response: {tool_calls}"
                )
            else:
                assistant_message = "Готов ответить на ваш запрос."
        result = ResumeEditResult(
            assistant_message=assistant_message or "Готов ответить на ваш запрос.",
            plan=todos_to_plan(state.get("todos")),
            warnings=["Агент не вернул структурированный ответ. Проверьте логи для диагностики."],
        )
        # Логируем обработку состояния
        await _log_state_processing(state, structured, result, unit_of_work, user_id)
        return result

    assistant_message = structured.get("assistant_message") or _messages_to_last_ai_content(messages)
    if not assistant_message:
        logger.warning(
            f"[state_to_resume_edit_result] structured response exists but assistant_message is empty. "
            f"structured keys: {list(structured.keys()) if structured else 'None'}"
        )
        assistant_message = "Готов ответить на ваш запрос."
    questions = _normalize_questions(structured.get("questions", []) or [])
    patches = _normalize_patches(structured.get("patches", []) or [])
    warnings = structured.get("warnings", []) or []

    result = ResumeEditResult(
        assistant_message=assistant_message,
        questions=questions,
        patches=patches,
        plan=todos_to_plan(state.get("todos")),
        warnings=warnings,
    )
    
    # Логируем обработку состояния
    await _log_state_processing(state, structured, result, unit_of_work, user_id)
    
    return result
