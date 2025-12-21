"""Исключение при превышении лимита откликов."""

from __future__ import annotations


class SubscriptionLimitExceededError(Exception):
    """Исключение, которое выбрасывается при превышении лимита откликов.

    Содержит информацию о текущем количестве откликов, лимите плана
    и времени до следующего сброса лимита.
    """

    def __init__(
        self,
        count: int,
        limit: int,
        seconds_until_reset: int | None = None,
        message: str | None = None,
    ) -> None:
        """Инициализация исключения.

        Args:
            count: Текущее количество откликов.
            limit: Лимит откликов плана.
            seconds_until_reset: Секунд до следующего сброса лимита (опционально).
            message: Кастомное сообщение об ошибке (опционально).
        """
        self.count = count
        self.limit = limit
        self.seconds_until_reset = seconds_until_reset

        if message is None:
            if seconds_until_reset is not None:
                hours = seconds_until_reset // 3600
                minutes = (seconds_until_reset % 3600) // 60
                message = (
                    f"Лимит откликов исчерпан: {count}/{limit}. "
                    f"Сброс через {hours}ч {minutes}м"
                )
            else:
                message = f"Лимит откликов исчерпан: {count}/{limit}"

        super().__init__(message)
