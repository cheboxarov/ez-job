"""Базовый класс для всех LLM-агентов с retry логикой."""

from __future__ import annotations

from abc import ABC
from typing import Any, Callable, TypeVar, Dict, List

from openai import AsyncOpenAI
from loguru import logger

from config import OpenAIConfig
from domain.exceptions.agent_exceptions import AgentParseError

T = TypeVar("T")


class BaseAgent(ABC):
    """Базовый класс для всех LLM-агентов с retry логикой."""

    MAX_RETRIES = 3

    def __init__(self, config: OpenAIConfig, client: AsyncOpenAI | None = None) -> None:
        """Инициализация базового агента.

        Args:
            config: Конфигурация OpenAI.
            client: Опциональный клиент AsyncOpenAI (для тестирования).
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

    async def _call_llm_with_retry(
        self,
        messages: List[Dict[str, Any]],
        parse_func: Callable[[str], T],
        validate_func: Callable[[T], bool] | None = None,
        temperature: float = 0.3,
        response_format: Dict[str, str] | None = None,
    ) -> T:
        """Вызов LLM с retry при ошибках парсинга.

        Args:
            messages: Сообщения для LLM.
            parse_func: Функция парсинга ответа -> результат.
            validate_func: Опциональная функция валидации (возвращает True если результат невалидный и нужен retry).
            temperature: Температура модели.
            response_format: Формат ответа (например {"type": "json_object"}).

        Returns:
            Результат парсинга.

        Raises:
            AgentParseError: Если после всех попыток парсинг не удался.
        """
        last_error: str | None = None

        for attempt in range(1, self.MAX_RETRIES + 1):
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

                return result

            except Exception as e:
                last_error = str(e)
                logger.warning(
                    f"[{self.AGENT_NAME}] Попытка {attempt}/{self.MAX_RETRIES} не удалась: {last_error}"
                )

                if attempt == self.MAX_RETRIES:
                    raise AgentParseError(self.AGENT_NAME, self.MAX_RETRIES, last_error) from e

        raise AgentParseError(self.AGENT_NAME, self.MAX_RETRIES, last_error)
