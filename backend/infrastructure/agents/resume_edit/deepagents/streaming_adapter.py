"""Адаптер стриминга DeepAgent к WebSocket протоколу."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from langchain_core.messages import AIMessage
from langgraph.graph.state import CompiledStateGraph

from infrastructure.agents.resume_edit.deepagents.state_mapper import todos_to_plan


StreamCallback = Callable[[str], Awaitable[None]] | Callable[[str], None]
PlanCallback = Callable[[list[dict]], Awaitable[None]] | Callable[[list[dict]], None]


async def stream_deep_agent(
    agent: CompiledStateGraph,
    input_data: dict,
    *,
    on_chunk: StreamCallback | None = None,
    on_plan: PlanCallback | None = None,
) -> dict:
    """Запустить DeepAgent в режиме стриминга и вернуть итоговое состояние."""
    last_state: dict | None = None
    last_ai_text = ""
    last_todos: list[dict] | None = None

    async for chunk in agent.astream(input_data, stream_mode="values"):
        last_state = chunk

        if on_plan and "todos" in chunk and chunk.get("todos") is not None:
            if last_todos != chunk["todos"]:
                last_todos = list(chunk["todos"])
                plan = todos_to_plan(chunk["todos"])
                result = on_plan(plan)
                if hasattr(result, "__await__"):
                    await result  # type: ignore[misc]

        if on_chunk and "messages" in chunk:
            messages = chunk.get("messages") or []
            latest_ai_text = ""
            for msg in reversed(messages):
                if isinstance(msg, AIMessage) and msg.content:
                    latest_ai_text = str(msg.content)
                    break
            if latest_ai_text and latest_ai_text.startswith(last_ai_text):
                delta = latest_ai_text[len(last_ai_text) :]
            else:
                delta = latest_ai_text
            if delta:
                last_ai_text = latest_ai_text
                result = on_chunk(delta)
                if hasattr(result, "__await__"):
                    await result  # type: ignore[misc]

    return last_state or {}


async def stream_deep_agent_to_websocket(
    *,
    agent: CompiledStateGraph,
    input_data: dict,
    websocket_send: Callable[[str, dict], Awaitable[None]],
    send_plan_updates: bool = True,
) -> dict:
    """Адаптировать LangGraph streaming к WebSocket формату."""

    async def _send_chunk(chunk: str) -> None:
        await websocket_send("streaming", {"chunk": chunk, "is_complete": False})

    async def _send_plan(plan: list[dict]) -> None:
        if send_plan_updates:
            await websocket_send("plan", {"plan": plan})

    final_state = await stream_deep_agent(
        agent,
        input_data,
        on_chunk=_send_chunk,
        on_plan=_send_plan if send_plan_updates else None,
    )

    await websocket_send("streaming", {"chunk": "", "is_complete": True})
    return final_state
