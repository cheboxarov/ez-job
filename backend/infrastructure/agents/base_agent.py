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
                    "model": self._config.model,
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

                if validate_func and validate_func(result):
                    raise ValueError("Невалидный результат парсинга")

                status = "success"
                last_error = None

                # Логируем успешную попытку
                await self._log_llm_call(
                    call_id=call_id,
                    attempt_number=attempt,
                    messages=messages,
                    response=content,
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

                # Логируем неудачную попытку
                await self._log_llm_call(
                    call_id=call_id,
                    attempt_number=attempt,
                    messages=messages,
                    response=content or "",
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
            if response_obj and hasattr(response_obj, "usage") and response_obj.usage:
                prompt_tokens = getattr(response_obj.usage, "prompt_tokens", None)
                completion_tokens = getattr(response_obj.usage, "completion_tokens", None)
                total_tokens = getattr(response_obj.usage, "total_tokens", None)

            # Вычисляем размер ответа в байтах
            response_size_bytes = len(response.encode("utf-8")) if response else None

            llm_call = LlmCall(
                id=uuid4(),
                call_id=call_id,
                attempt_number=attempt_number,
                agent_name=self.AGENT_NAME,
                model=self._config.model,
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
                cost_usd=None,  # Расчет стоимости происходит на фронтенде
                context=context,
                created_at=datetime.now(),  # Будет перезаписано БД
            )

            await self._unit_of_work.llm_call_repository.create(llm_call)
        except Exception as e:
            # Логирование не должно прерывать выполнение основного кода
            logger.error(
                f"[{self.AGENT_NAME}] Ошибка при логировании вызова LLM в БД: {e}",
                exc_info=True,
            )