"""Главный DeepAgent для редактирования резюме."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from deepagents import create_deep_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_openai import ChatOpenAI
from loguru import logger
from pydantic import BaseModel, Field

from config import OpenAIConfig
from domain.interfaces.resume_editor_port import ResumeEditorPort
from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from infrastructure.agents.llm_call_logger import LlmCallLogger
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
    GeneratePatchesInput,
)
from infrastructure.agents.resume_edit.tools.deepagents_question_tool import (
    create_deepagents_question_tool,
    GenerateQuestionsInput,
)
from infrastructure.agents.resume_edit.tools.format_resume_tool import (
    format_resume_tool,
)
from infrastructure.agents.resume_edit.tools.rule_check_tool import load_resume_rules
from infrastructure.agents.resume_edit.tools.state_injector import StateInjectorTool
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


def init_chat_model_from_config(
    config: OpenAIConfig, unit_of_work: UnitOfWorkPort | None = None
) -> ChatOpenAI:
    """Инициализировать ChatOpenAI из конфигурации."""
    if not config.api_key:
        raise RuntimeError("OpenAIConfig.api_key не задан (проверь конфиг/окружение)")
    model_name = config.get_model_for_agent("ResumeEditDeepAgent")
    callbacks = []
    if unit_of_work:
        callbacks.append(
            LlmCallLogger(
                unit_of_work=unit_of_work,
                agent_name="ResumeEditDeepAgent",
                model=model_name,
                temperature=0.4,
                context={"use_case": "resume_edit_deep_agent"},
            )
        )
    return ChatOpenAI(
        model=model_name,
        base_url=config.base_url,
        api_key=config.api_key,
        temperature=0.4,
        callbacks=callbacks or None,
    )


def create_resume_edit_deep_agent(
    config: OpenAIConfig, unit_of_work: UnitOfWorkPort | None = None
):
    """Создать главный DeepAgent для редактирования резюме."""
    main_prompt = _load_main_prompt()
    model = init_chat_model_from_config(config, unit_of_work=unit_of_work)

    patch_tool = create_deepagents_patch_tool(config, unit_of_work=unit_of_work)
    question_tool = create_deepagents_question_tool(config, unit_of_work=unit_of_work)

    patch_tool = StateInjectorTool(
        patch_tool,
        injections={"resume_text": "resume_text", "user_id": "user_id"},
        args_schema=GeneratePatchesInput,
    ).tool
    question_tool = StateInjectorTool(
        question_tool,
        injections={"resume_text": "resume_text", "user_id": "user_id"},
        args_schema=GenerateQuestionsInput,
    ).tool

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

    def __init__(
        self,
        config: OpenAIConfig,
        agent=None,
        unit_of_work: UnitOfWorkPort | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._agent = agent or create_resume_edit_deep_agent(
            config, unit_of_work=unit_of_work
        )

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
            user_id=user_id,
        )

        if streaming_callback:
            async def _on_chunk(chunk: str) -> None:
                try:
                    streaming_callback(chunk)
                except Exception as exc:
                    logger.warning(
                        f"Ошибка в streaming callback при редактировании резюме: "
                        f"user_id={user_id}, error={exc}"
                    )
                    return

            run_metadata = {"user_id": str(user_id)} if user_id else None
            final_state = await stream_deep_agent(
                self._agent,
                input_state,
                on_chunk=_on_chunk,
                run_metadata=run_metadata,
            )
        else:
            run_metadata = {"user_id": str(user_id)} if user_id else None
            config = {"metadata": run_metadata} if run_metadata else None
            final_state = await self._agent.ainvoke(input_state, config=config)

        return await state_to_resume_edit_result(
            final_state,
            unit_of_work=self._unit_of_work,
            user_id=user_id,
        )
