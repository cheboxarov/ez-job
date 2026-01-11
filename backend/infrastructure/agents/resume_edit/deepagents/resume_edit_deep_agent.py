"""Главный DeepAgent для редактирования резюме."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from deepagents import create_deep_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from config import OpenAIConfig
from domain.interfaces.resume_editor_port import ResumeEditorPort
from infrastructure.agents.resume_edit.deepagents.chat_subagent import (
    create_chat_subagent,
)
from infrastructure.agents.resume_edit.deepagents.patch_subagent import (
    create_patch_subagent,
)
from infrastructure.agents.resume_edit.deepagents.question_subagent import (
    create_question_subagent,
)
from infrastructure.agents.resume_edit.deepagents.state_mapper import (
    build_agent_input,
    get_current_task,
    state_to_resume_edit_result,
)
from infrastructure.agents.resume_edit.deepagents.streaming_adapter import (
    stream_deep_agent,
)
from infrastructure.agents.resume_edit.tools.deepagents_patch_tool import (
    create_deepagents_patch_tool,
)
from infrastructure.agents.resume_edit.tools.deepagents_question_tool import (
    create_deepagents_question_tool,
)
from infrastructure.agents.resume_edit.tools.format_resume_tool import (
    format_resume_tool,
)
from infrastructure.agents.resume_edit.tools.rule_check_tool import load_resume_rules
from infrastructure.agents.resume_edit.tools.validate_patch_tool import (
    validate_resume_patches_tool,
)


class ResumeEditQuestionModel(BaseModel):
    id: str
    text: str
    required: bool = True
    suggested_answers: list[str] = Field(default_factory=list)
    allow_multiple: bool = False


class ResumeEditPatchModel(BaseModel):
    id: str | None = None
    type: Literal["replace", "insert", "delete"]
    start_line: int
    end_line: int
    old_text: str
    new_text: str | None = None
    reason: str = ""


class ResumeEditStructuredResponse(BaseModel):
    action: Literal["ask_question", "generate_patches", "chat"]
    assistant_message: str
    questions: list[ResumeEditQuestionModel] = Field(default_factory=list)
    patches: list[ResumeEditPatchModel] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


def _load_main_prompt() -> str:
    prompt_path = (
        Path(__file__).parent.parent.parent / "prompts" / "resume_edit_deep_agent.md"
    )
    base_prompt = prompt_path.read_text(encoding="utf-8")
    resume_rules = load_resume_rules()
    return f"{base_prompt}\n\n## Правила HH\n{resume_rules}"


def init_chat_model_from_config(config: OpenAIConfig) -> ChatOpenAI:
    """Инициализировать ChatOpenAI из конфигурации."""
    if not config.api_key:
        raise RuntimeError("OpenAIConfig.api_key не задан (проверь конфиг/окружение)")
    model_name = config.resume_edit_model or config.model
    return ChatOpenAI(
        model=model_name,
        base_url=config.base_url,
        api_key=config.api_key,
        temperature=0.2,
    )


def create_resume_edit_deep_agent(config: OpenAIConfig):
    """Создать главный DeepAgent для редактирования резюме."""
    main_prompt = _load_main_prompt()
    model = init_chat_model_from_config(config)

    patch_tool = create_deepagents_patch_tool(config)
    question_tool = create_deepagents_question_tool(config)

    subagents = [
        create_question_subagent([question_tool, format_resume_tool]),
        create_patch_subagent(
            [patch_tool, format_resume_tool, validate_resume_patches_tool]
        ),
        create_chat_subagent([format_resume_tool]),
    ]

    return create_deep_agent(
        model=model,
        system_prompt=main_prompt,
        subagents=subagents,
        tools=[format_resume_tool],
        response_format=ToolStrategy(schema=ResumeEditStructuredResponse),
    )


class ResumeEditDeepAgentAdapter(ResumeEditorPort):
    """Адаптер DeepAgent к интерфейсу ResumeEditorPort."""

    def __init__(self, config: OpenAIConfig, agent=None) -> None:
        self._agent = agent or create_resume_edit_deep_agent(config)

    async def generate_edits(
        self,
        resume_text: str,
        user_message: str,
        history: list[dict] | None = None,
        current_plan: list[dict] | None = None,
        current_task: dict | None = None,
        user_id=None,
        streaming_callback=None,
        session_logger=None,
    ):
        if current_task is None:
            current_task = get_current_task(current_plan)

        input_state = build_agent_input(
            resume_text=resume_text,
            user_message=user_message,
            history=history,
            current_plan=current_plan,
            current_task=current_task,
        )

        if streaming_callback:
            async def _on_chunk(chunk: str) -> None:
                try:
                    streaming_callback(chunk)
                except Exception:
                    return

            final_state = await stream_deep_agent(
                self._agent,
                input_state,
                on_chunk=_on_chunk,
            )
        else:
            final_state = await self._agent.ainvoke(input_state)

        return state_to_resume_edit_result(final_state)
