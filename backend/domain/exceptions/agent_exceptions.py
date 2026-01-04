"""Исключения для агентов."""

from __future__ import annotations


class AgentParseError(Exception):
    """Исключение при неудачном парсинге ответа агента после всех retry попыток."""

    def __init__(self, agent_name: str, attempts: int, last_error: str | None = None) -> None:
        """Инициализация исключения.

        Args:
            agent_name: Имя агента.
            attempts: Количество попыток.
            last_error: Последняя ошибка (опционально).
        """
        self.agent_name = agent_name
        self.attempts = attempts
        self.last_error = last_error
        message = f"Агент {agent_name} не смог распарсить ответ после {attempts} попыток"
        if last_error:
            message += f": {last_error}"
        super().__init__(message)
