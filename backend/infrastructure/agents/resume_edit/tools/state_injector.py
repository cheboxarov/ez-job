"""Helpers for injecting LangGraph state into tool calls."""

from __future__ import annotations

from typing import Any

from langchain.tools import ToolRuntime
from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel


class StateInjectorTool:
    """Wrap a tool and inject missing args from runtime state."""

    def __init__(
        self,
        original_tool: BaseTool,
        injections: dict[str, str],
        args_schema: type[BaseModel] | None = None,
    ) -> None:
        self._original_tool = original_tool
        self._injections = injections
        self._args_schema = args_schema
        self._wrapped_tool = self._build_tool()

    @property
    def tool(self) -> BaseTool:
        return self._wrapped_tool

    def _build_tool(self) -> BaseTool:
        @tool(
            self._original_tool.name,
            args_schema=self._args_schema,
            description=self._original_tool.description,
        )
        async def _injected_tool(runtime: ToolRuntime, **kwargs: Any) -> Any:
            state = getattr(runtime, "state", {}) if runtime else {}
            if isinstance(state, dict):
                for param_name, state_key in self._injections.items():
                    if param_name not in kwargs and state_key in state:
                        value = state.get(state_key)
                        if value is not None:
                            kwargs[param_name] = value
            config = runtime.config if runtime else None
            return await self._original_tool.ainvoke(kwargs, config=config)

        return _injected_tool
