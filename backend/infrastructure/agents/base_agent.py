"""Базовый класс для всех LLM-агентов с retry логикой."""

from __future__ import annotations

import time
from abc import ABC
from datetime import datetime
from typing import Any, Callable, TypeVar, Dict, List
from uuid import UUID, uuid4

from openai import AsyncOpenAI
from loguru import logger

from config import OpenAIConfig
from domain.exceptions.agent_exceptions import AgentParseError
from domain.entities.llm_call import LlmCall
from domain.interfaces.unit_of_work_port import UnitOfWorkPort

T = TypeVar("T")


def _format_response_with_diagnostics(
    original_response: str,
    parsed_result: Any | None = None,
    validation_passed: bool | None = None,
    validation_reason: str | None = None,
    error_type: str | None = None,
    error_message: str | None = None,
    attempt_number: int | None = None,
) -> str:
    """Форматировать response с диагностической информацией.
    
    Args:
        original_response: Оригинальный ответ от LLM.
        parsed_result: Результат парсинга (если успешен).
        validation_passed: Прошла ли валидация.
        validation_reason: Причина неудачной валидации.
        error_type: Тип ошибки.
        error_message: Текст ошибки.
        attempt_number: Номер попытки.
    
    Returns:
        Отформатированный response с диагностической информацией.
    """
    parts = [original_response]
    
    diagnostics = []
    if attempt_number:
        diagnostics.append(f"attempt_number: {attempt_number}")
    if parsed_result is not None:
        diagnostics.append(f"parsed_successfully: true")
        diagnostics.append(f"parsed_result_type: {type(parsed_result).__name__}")
        try:
            result_preview = str(parsed_result)[:500]
            diagnostics.append(f"parsed_result_preview: {result_preview}")
        except Exception:
            diagnostics.append(f"parsed_result_preview: <unable to stringify>")
    else:
        diagnostics.append(f"parsed_successfully: false")
    
    if validation_passed is not None:
        diagnostics.append(f"validation_passed: {validation_passed}")
        if not validation_passed and validation_reason:
            diagnostics.append(f"validation_failed_reason: {validation_reason}")
    
    if error_type:
        diagnostics.append(f"error_type: {error_type}")
    if error_message:
        diagnostics.append(f"error_message: {error_message}")
    
    if diagnostics:
        parts.append("\n\n=== ДИАГНОСТИКА ===")
        parts.extend(diagnostics)
    
    return "\n".join(parts)


class BaseAgent(ABC):
    """Базовый класс для всех LLM-агентов с retry логикой."""

    MAX_RETRIES = 3

    def __init__(
        self,
        config: OpenAIConfig,
        client: AsyncOpenAI | None = None,
        unit_of_work: UnitOfWorkPort | None = None,
    ) -> None:
        """Инициализация базового агента.

        Args:
            config: Конфигурация OpenAI.
            client: Опциональный клиент AsyncOpenAI (для тестирования).
            unit_of_work: Опциональный UnitOfWork для логирования вызовов в БД.
        """
        self._config = config
        if client is None:
            api_key = self._config.api_key
            if not api_key:
                raise RuntimeError("OpenAIConfig.api_key не задан (проверь конфиг/окружение)")
            client = AsyncOpenAI(
                base_url=self._config.base_url,
                api_key=api_key,
            )
        self._client = client
        self._unit_of_work = unit_of_work

    def set_unit_of_work(self, unit_of_work: UnitOfWorkPort | None) -> None:
        """Обновить UnitOfWork для логирования вызовов LLM.

        Args:
            unit_of_work: Новый UnitOfWork для логирования (может быть None).
        """
        self._unit_of_work = unit_of_work

    async def _call_llm_with_retry(
        self,
        messages: List[Dict[str, Any]],
        parse_func: Callable[[str], T],
        validate_func: Callable[[T], bool] | None = None,
        temperature: float = 0.3,
        response_format: Dict[str, str] | None = None,
        user_id: UUID | None = None,
        context: dict[str, Any] | None = None,
    ) -> T:
        """Вызов LLM с retry при ошибках парсинга.

        Args:
            messages: Сообщения для LLM.
            parse_func: Функция парсинга ответа -> результат.
            validate_func: Опциональная функция валидации (возвращает True если результат невалидный и нужен retry).
            temperature: Температура модели.
            response_format: Формат ответа (например {"type": "json_object"}).
            user_id: ID пользователя для логирования (опционально).
            context: Дополнительный контекст для логирования (опционально).

        Returns:
            Результат парсинга.

        Raises:
            AgentParseError: Если после всех попыток парсинг не удался.
        """
        call_id = uuid4()
        last_error: str | None = None

        for attempt in range(1, self.MAX_RETRIES + 1):
            start_time = time.time()
            response = None
            content: str | None = None
            error_type: str | None = None
            error_message: str | None = None
            status = "error"

            try:
                kwargs: Dict[str, Any] = {
                    "model": self._config.get_model_for_agent(self.AGENT_NAME),
                    "messages": messages,
                    "temperature": temperature,
                }
                if response_format:
                    kwargs["response_format"] = response_format

                response = await self._client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content if response.choices else None

                if not content:
                    raise ValueError("Пустой ответ от модели")

                result = parse_func(content)
                validation_passed = None
                validation_reason = None
                
                if validate_func:
                    is_invalid = validate_func(result)
                    validation_passed = not is_invalid
                    if is_invalid:
                        validation_reason = "validate_func вернул True (результат невалидный)"

                if validation_passed is False:
                    raise ValueError("Невалидный результат парсинга")

                status = "success"
                last_error = None

                # Форматируем response с диагностикой
                response_with_diagnostics = _format_response_with_diagnostics(
                    original_response=content,
                    parsed_result=result,
                    validation_passed=validation_passed,
                    validation_reason=validation_reason,
                    attempt_number=attempt,
                )

                # Логируем успешную попытку
                await self._log_llm_call(
                    call_id=call_id,
                    attempt_number=attempt,
                    messages=messages,
                    response=response_with_diagnostics,
                    temperature=temperature,
                    response_format=response_format,
                    user_id=user_id,
                    context=context,
                    status=status,
                    error_type=None,
                    error_message=None,
                    start_time=start_time,
                    response_obj=response,
                )

                return result

            except Exception as e:
                last_error = str(e)
                error_type = type(e).__name__
                error_message = str(e)
                status = "error"

                logger.warning(
                    f"[{self.AGENT_NAME}] Попытка {attempt}/{self.MAX_RETRIES} не удалась: {last_error}"
                )

                # Определяем, был ли парсинг успешным до ошибки
                parsed_result = None
                validation_passed = None
                validation_reason = None
                try:
                    if content:
                        parsed_result = parse_func(content)
                        if validate_func:
                            is_invalid = validate_func(parsed_result)
                            validation_passed = not is_invalid
                            if is_invalid:
                                validation_reason = "validate_func вернул True (результат невалидный)"
                except Exception as exc:
                    # Парсинг не удался, это нормально для ошибок
                    logger.debug(
                        f"[{self.AGENT_NAME}] Парсинг не удался при обработке ошибки (ожидаемое поведение): {exc}"
                    )

                # Форматируем response с диагностикой
                response_with_diagnostics = _format_response_with_diagnostics(
                    original_response=content or "",
                    parsed_result=parsed_result,
                    validation_passed=validation_passed,
                    validation_reason=validation_reason,
                    error_type=error_type,
                    error_message=error_message,
                    attempt_number=attempt,
                )

                # Логируем неудачную попытку
                await self._log_llm_call(
                    call_id=call_id,
                    attempt_number=attempt,
                    messages=messages,
                    response=response_with_diagnostics,
                    temperature=temperature,
                    response_format=response_format,
                    user_id=user_id,
                    context=context,
                    status=status,
                    error_type=error_type,
                    error_message=error_message,
                    start_time=start_time,
                    response_obj=response,
                )

                if attempt == self.MAX_RETRIES:
                    raise AgentParseError(self.AGENT_NAME, self.MAX_RETRIES, last_error) from e

        raise AgentParseError(self.AGENT_NAME, self.MAX_RETRIES, last_error)

    async def _log_llm_call(
        self,
        call_id: UUID,
        attempt_number: int,
        messages: List[Dict[str, Any]],
        response: str,
        temperature: float,
        response_format: Dict[str, str] | None,
        user_id: UUID | None,
        context: dict[str, Any] | None,
        status: str,
        error_type: str | None,
        error_message: str | None,
        start_time: float,
        response_obj: Any | None,
    ) -> None:
        """Логировать вызов LLM в базу данных.

        Args:
            call_id: Идентификатор вызова.
            attempt_number: Номер попытки.
            messages: Сообщения для LLM.
            response: Ответ от LLM.
            temperature: Температура модели.
            response_format: Формат ответа.
            user_id: ID пользователя.
            context: Дополнительный контекст.
            status: Статус ('success' или 'error').
            error_type: Тип ошибки.
            error_message: Текст ошибки.
            start_time: Время начала вызова.
            response_obj: Объект ответа от API (для извлечения токенов).
        """
        if not self._unit_of_work:
            logger.warning(
                f"[{self.AGENT_NAME}] unit_of_work не установлен, пропускаем логирование LLM-вызова"
            )
            return

        try:
            end_time = time.time()
            duration_ms = int((end_time - start_time) * 1000)

            # Извлекаем информацию о токенах из response
            prompt_tokens = None
            completion_tokens = None
            total_tokens = None
            cost_usd = None
            if response_obj and hasattr(response_obj, "usage") and response_obj.usage:
                prompt_tokens = getattr(response_obj.usage, "prompt_tokens", None)
                completion_tokens = getattr(response_obj.usage, "completion_tokens", None)
                total_tokens = getattr(response_obj.usage, "total_tokens", None)
            
            # Пытаемся извлечь cost из response_metadata или других полей
            if response_obj:
                # Проверяем response_metadata
                if hasattr(response_obj, "response_metadata"):
                    metadata = response_obj.response_metadata
                    if isinstance(metadata, dict):
                        # Проверяем token_usage.cost или cost напрямую
                        token_usage = metadata.get("token_usage", {})
                        if isinstance(token_usage, dict):
                            cost_usd = token_usage.get("cost")
                        if cost_usd is None:
                            cost_usd = metadata.get("cost")
                # Проверяем другие возможные места
                if cost_usd is None and hasattr(response_obj, "llm_output"):
                    llm_output = response_obj.llm_output
                    if isinstance(llm_output, dict):
                        token_usage = llm_output.get("token_usage", {})
                        if isinstance(token_usage, dict):
                            cost_usd = token_usage.get("cost")
                        if cost_usd is None:
                            cost_usd = llm_output.get("cost")

            # Вычисляем размер ответа в байтах
            response_size_bytes = len(response.encode("utf-8")) if response else None

            llm_call = LlmCall(
                id=uuid4(),
                call_id=call_id,
                attempt_number=attempt_number,
                agent_name=self.AGENT_NAME,
                model=self._config.get_model_for_agent(self.AGENT_NAME),
                user_id=user_id,
                prompt=messages,
                response=response,
                temperature=temperature,
                response_format=response_format,
                status=status,
                error_type=error_type,
                error_message=error_message,
                duration_ms=duration_ms,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                response_size_bytes=response_size_bytes,
                cost_usd=cost_usd,
                context=context,
                created_at=datetime.now(),  # Будет перезаписано БД
            )

            # Используем standalone репозиторий для логирования, так как логирование не должно
            # держать транзакцию открытой во время LLM вызова
            await self._unit_of_work.standalone_llm_call_repository.create(llm_call)
        except Exception as e:
            # Логирование не должно прерывать выполнение основного кода
            logger.error(
                f"[{self.AGENT_NAME}] Ошибка при логировании вызова LLM в БД: {e}",
                exc_info=True,
            )