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
    resume_text: str,
    user_message: str,
    history: list[dict] | None,
    current_plan: list[dict] | None,
    current_task: dict | None,
) -> dict:
    """Сформировать входное состояние для DeepAgent."""
    messages = history_to_messages(history)
    messages.append(
        HumanMessage(
            content=build_user_prompt(
                resume_text, user_message, current_plan, current_task, history
            )
        )
    )
    return {
        "messages": messages,
        "todos": plan_to_todos(current_plan),
        "resume_text": resume_text,
        "current_plan": current_plan or [],
        "current_task": current_task,
        "history": history or [],
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
        except Exception:
            continue
    return patches


def state_to_resume_edit_result(state: dict) -> ResumeEditResult:
    """Преобразовать состояние DeepAgent в ResumeEditResult."""
    structured = _parse_structured_response(state.get("structured_response"))
    messages = state.get("messages", [])

    if structured is None:
        fallback = _messages_to_last_ai_content(messages)
        try:
            structured = json.loads(fallback) if fallback else None
        except json.JSONDecodeError:
            structured = None

    if not structured:
        assistant_message = _messages_to_last_ai_content(messages)
        return ResumeEditResult(
            assistant_message=assistant_message or "Готов ответить на ваш запрос.",
            plan=todos_to_plan(state.get("todos")),
        )

    assistant_message = structured.get("assistant_message") or _messages_to_last_ai_content(messages)
    if not assistant_message:
        assistant_message = "Готов ответить на ваш запрос."
    questions = _normalize_questions(structured.get("questions", []) or [])
    patches = _normalize_patches(structured.get("patches", []) or [])
    warnings = structured.get("warnings", []) or []

    return ResumeEditResult(
        assistant_message=assistant_message,
        questions=questions,
        patches=patches,
        plan=todos_to_plan(state.get("todos")),
        warnings=warnings,
    )
