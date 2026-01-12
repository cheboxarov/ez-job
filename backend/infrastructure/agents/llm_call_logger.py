"""Callback logger for persisting LLM calls to the database."""

from __future__ import annotations

import time
from typing import Any
from uuid import UUID, uuid4

from loguru import logger
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.messages import BaseMessage
from datetime import datetime

from domain.entities.llm_call import LlmCall
from domain.interfaces.unit_of_work_port import UnitOfWorkPort


class LlmCallLogger(AsyncCallbackHandler):
    """Async callback handler for logging LLM calls."""

    def __init__(
        self,
        *,
        unit_of_work: UnitOfWorkPort | None,
        agent_name: str,
        model: str,
        temperature: float | None = None,
        response_format: dict[str, str] | None = None,
        context: dict[str, Any] | None = None,
        user_id: UUID | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._agent_name = agent_name
        self._model = model
        self._temperature = temperature
        self._response_format = response_format
        self._context = context
        self._user_id = user_id
        self._calls: dict[str, dict[str, Any]] = {}

    async def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[BaseMessage]] | list[BaseMessage],
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        if not self._unit_of_work:
            return
        prompt = self._normalize_messages(messages)
        user_id, context = self._extract_metadata(kwargs)
        self._calls[str(run_id)] = {
            "call_id": uuid4(),
            "start_time": time.time(),
            "prompt": prompt,
            "user_id": user_id,
            "context": context,
        }

    async def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        if not self._unit_of_work:
            return
        prompt = [{"role": "user", "content": p} for p in prompts or []]
        user_id, context = self._extract_metadata(kwargs)
        self._calls[str(run_id)] = {
            "call_id": uuid4(),
            "start_time": time.time(),
            "prompt": prompt,
            "user_id": user_id,
            "context": context,
        }

    async def on_chat_model_end(
        self,
        response: Any,
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        await self.on_llm_end(response, run_id=run_id, **kwargs)

    async def on_llm_end(
        self,
        response: Any,
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        if not self._unit_of_work:
            return
        info = self._calls.pop(str(run_id), None)
        if not info:
            return
        response_text = self._extract_response_text(response)
        
        # Добавляем дополнительную диагностику из llm_output и response объекта
        additional_diagnostics = []
        llm_output = getattr(response, "llm_output", None)
        if llm_output:
            try:
                import json
                llm_output_str = json.dumps(llm_output, default=str, ensure_ascii=False)
                if len(llm_output_str) > 1000:
                    llm_output_str = llm_output_str[:1000] + "..."
                additional_diagnostics.append(f"llm_output_full: {llm_output_str}")
            except Exception as e:
                additional_diagnostics.append(f"llm_output_present_but_unserializable: {str(e)}")
        
        # Информация о response объекте
        response_attrs = [attr for attr in dir(response) if not attr.startswith("_")]
        additional_diagnostics.append(f"response_attributes_count: {len(response_attrs)}")
        additional_diagnostics.append(f"response_attributes_sample: {', '.join(response_attrs[:10])}")
        
        if additional_diagnostics:
            response_text += "\n\n=== ДОПОЛНИТЕЛЬНАЯ ДИАГНОСТИКА (on_llm_end) ==="
            response_text += "\n" + "\n".join(additional_diagnostics)
        
        await self._write_llm_call(
            call_id=info["call_id"],
            attempt_number=1,
            prompt=info["prompt"],
            response_text=response_text,
            status="success",
            error_type=None,
            error_message=None,
            start_time=info["start_time"],
            llm_output=llm_output,
            user_id=info.get("user_id"),
            context=info.get("context"),
        )

    async def on_llm_error(
        self,
        error: Exception,
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        if not self._unit_of_work:
            return
        info = self._calls.pop(str(run_id), None) or {
            "call_id": uuid4(),
            "start_time": time.time(),
            "prompt": [],
        }
        await self._write_llm_call(
            call_id=info["call_id"],
            attempt_number=1,
            prompt=info["prompt"],
            response_text="",
            status="error",
            error_type=type(error).__name__,
            error_message=str(error),
            start_time=info["start_time"],
            llm_output=None,
            user_id=info.get("user_id"),
            context=info.get("context"),
        )

    async def on_chat_model_error(
        self,
        error: Exception,
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        await self.on_llm_error(error, run_id=run_id, **kwargs)

    def _normalize_messages(
        self, messages: list[list[BaseMessage]] | list[BaseMessage]
    ) -> list[dict[str, Any]]:
        if not messages:
            return []
        if isinstance(messages[0], list):
            messages = messages[0]
        prompt: list[dict[str, Any]] = []
        for msg in messages:  # type: ignore[assignment]
            if isinstance(msg, dict):
                role = msg.get("role") or msg.get("type") or "user"
                prompt.append({"role": role, "content": msg.get("content", "")})
                continue
            role = getattr(msg, "type", None) or getattr(msg, "role", None) or "user"
            role = self._map_role(role)
            content = getattr(msg, "content", None)
            prompt.append({"role": role, "content": content if content is not None else str(msg)})
        return prompt

    def _map_role(self, role: str) -> str:
        if role == "human":
            return "user"
        if role == "ai":
            return "assistant"
        if role in {"system", "tool", "user", "assistant"}:
            return role
        return "user"

    def _extract_response_text(self, response: Any) -> str:
        """Извлечь текст ответа и добавить диагностическую информацию о структуре."""
        import json
        
        diagnostics_parts = []
        diagnostics_parts.append(f"response_type: {type(response).__name__}")
        
        generations = getattr(response, "generations", None) or []
        diagnostics_parts.append(f"generations_count: {len(generations)}")
        
        if not generations:
            diagnostics_parts.append("generations_empty: true")
            return self._format_response_with_diagnostics("", diagnostics_parts)
        
        first = generations[0][0] if generations[0] else None
        if first is None:
            diagnostics_parts.append("first_generation_empty: true")
            return self._format_response_with_diagnostics("", diagnostics_parts)
        
        diagnostics_parts.append(f"first_generation_type: {type(first).__name__}")
        
        message = getattr(first, "message", None)
        content = ""
        tool_calls_data = []
        
        if message is not None:
            # Извлекаем content
            if getattr(message, "content", None) is not None:
                content = str(message.content)
                diagnostics_parts.append("extraction_method: message.content")
            
            # КРИТИЧЕСКИ ВАЖНО: Извлекаем tool calls, особенно для ToolStrategy
            tool_calls = getattr(message, "tool_calls", None) or []
            if tool_calls:
                diagnostics_parts.append(f"tool_calls_count: {len(tool_calls)}")
                for tc in tool_calls:
                    tc_data = {}
                    # Извлекаем name
                    if hasattr(tc, "name"):
                        tc_data["name"] = tc.name
                    elif isinstance(tc, dict):
                        tc_data["name"] = tc.get("name")
                    else:
                        tc_data["name"] = str(getattr(tc, "name", "unknown"))
                    
                    # Извлекаем id
                    if hasattr(tc, "id"):
                        tc_data["id"] = tc.id
                    elif isinstance(tc, dict):
                        tc_data["id"] = tc.get("id")
                    
                    # Извлекаем args
                    if hasattr(tc, "args"):
                        try:
                            # Пытаемся сериализовать args
                            args_str = json.dumps(tc.args, default=str, ensure_ascii=False)
                            if len(args_str) > 1000:
                                args_str = args_str[:1000] + "..."
                            tc_data["args"] = args_str
                        except Exception:
                            tc_data["args"] = str(tc.args)[:500]
                    elif isinstance(tc, dict) and "args" in tc:
                        try:
                            args_str = json.dumps(tc["args"], default=str, ensure_ascii=False)
                            if len(args_str) > 1000:
                                args_str = args_str[:1000] + "..."
                            tc_data["args"] = args_str
                        except Exception:
                            tc_data["args"] = str(tc["args"])[:500]
                    else:
                        # Пытаемся извлечь из других атрибутов
                        tc_data["raw"] = str(tc)[:500]
                    
                    tool_calls_data.append(tc_data)
                
                # Если content пустой, но есть tool calls - это структурированный ответ через ToolStrategy
                if not content and tool_calls_data:
                    diagnostics_parts.append("structured_response_via_tool_call: true")
                    # Форматируем tool calls для логирования
                    try:
                        tool_calls_json = json.dumps(tool_calls_data, default=str, ensure_ascii=False, indent=2)
                        if len(tool_calls_json) > 3000:
                            tool_calls_json = tool_calls_json[:3000] + "..."
                        diagnostics_parts.append(f"tool_calls_data:\n{tool_calls_json}")
                        # Используем tool calls как основной контент, если content пустой
                        content = f"[STRUCTURED RESPONSE VIA TOOL CALL]\n{tool_calls_json}"
                    except Exception as e:
                        diagnostics_parts.append(f"tool_calls_serialization_error: {str(e)}")
                        content = f"[STRUCTURED RESPONSE VIA TOOL CALL - {len(tool_calls_data)} calls]"
                elif tool_calls_data:
                    # Логируем tool calls даже если есть content
                    try:
                        tool_calls_json = json.dumps(tool_calls_data, default=str, ensure_ascii=False, indent=2)
                        if len(tool_calls_json) > 2000:
                            tool_calls_json = tool_calls_json[:2000] + "..."
                        diagnostics_parts.append(f"tool_calls_data: {tool_calls_json}")
                    except Exception as exc:
                        logger.warning(
                            f"[LlmCallLogger] Не удалось сериализовать tool_calls_data: {exc}"
                        )
        
        if not content:
            # Пытаемся извлечь text напрямую
            text = getattr(first, "text", None)
            if text is not None:
                content = str(text)
                diagnostics_parts.append("extraction_method: text")
        
        if not content:
            # Дополнительная диагностика
            diagnostics_parts.append("extraction_failed: true")
            diagnostics_parts.append(f"first_attributes: {dir(first)[:10]}")
            
            # Попытка извлечь llm_output
            llm_output = getattr(response, "llm_output", None)
            if llm_output:
                try:
                    llm_output_str = json.dumps(llm_output, default=str, ensure_ascii=False)[:500]
                    diagnostics_parts.append(f"llm_output_preview: {llm_output_str}")
                except Exception:
                    diagnostics_parts.append("llm_output_present_but_unserializable: true")
        
        return self._format_response_with_diagnostics(content, diagnostics_parts)
    
    def _format_response_with_diagnostics(
        self, response_text: str, diagnostics_parts: list[str]
    ) -> str:
        """Форматировать response с диагностической информацией."""
        if not diagnostics_parts:
            return response_text
        
        parts = [response_text] if response_text else []
        parts.append("\n\n=== ДИАГНОСТИКА (LlmCallLogger) ===")
        parts.extend(diagnostics_parts)
        return "\n".join(parts)

    async def _write_llm_call(
        self,
        *,
        call_id: UUID,
        attempt_number: int,
        prompt: list[dict[str, Any]],
        response_text: str,
        status: str,
        error_type: str | None,
        error_message: str | None,
        start_time: float,
        llm_output: dict[str, Any] | None,
        user_id: UUID | None,
        context: dict[str, Any] | None,
    ) -> None:
        try:
            end_time = time.time()
            duration_ms = int((end_time - start_time) * 1000)
            prompt_tokens = None
            completion_tokens = None
            total_tokens = None
            cost_usd = None
            if llm_output and isinstance(llm_output, dict):
                token_usage = llm_output.get("token_usage") or {}
                prompt_tokens = token_usage.get("prompt_tokens")
                completion_tokens = token_usage.get("completion_tokens")
                total_tokens = token_usage.get("total_tokens")
                # Извлекаем cost из token_usage или из корня llm_output
                cost_usd = token_usage.get("cost")
                if cost_usd is None:
                    cost_usd = llm_output.get("cost")
            response_size_bytes = (
                len(response_text.encode("utf-8")) if response_text else None
            )
            llm_call = LlmCall(
                id=uuid4(),
                call_id=call_id,
                attempt_number=attempt_number,
                agent_name=self._agent_name,
                model=self._model,
                user_id=user_id or self._user_id,
                prompt=prompt,
                response=response_text,
                temperature=self._temperature or 0.0,
                response_format=self._response_format,
                status=status,
                error_type=error_type,
                error_message=error_message,
                duration_ms=duration_ms,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                response_size_bytes=response_size_bytes,
                cost_usd=cost_usd,
                context=context or self._context,
                created_at=datetime.now(),
            )
            await self._unit_of_work.standalone_llm_call_repository.create(llm_call)
        except Exception as exc:
            logger.error(
                f"[LlmCallLogger] Failed to log LLM call: {exc}",
                exc_info=True,
            )

    def _extract_metadata(self, kwargs: dict[str, Any]) -> tuple[UUID | None, dict[str, Any] | None]:
        metadata = kwargs.get("metadata") or {}
        user_id = self._normalize_user_id(metadata.get("user_id"))
        context = metadata.get("context")
        if context is not None and not isinstance(context, dict):
            context = {"value": context}
        return user_id, context

    def _normalize_user_id(self, value: Any) -> UUID | None:
        if not value:
            return None
        if isinstance(value, UUID):
            return value
        try:
            return UUID(str(value))
        except Exception:
            return None
