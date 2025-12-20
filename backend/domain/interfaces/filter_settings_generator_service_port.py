from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities.suggested_user_filter_settings import SuggestedUserFilterSettings


class FilterSettingsGeneratorServicePort(ABC):
    """Порт сервиса генерации предложенных настроек фильтров пользователя."""

    @abstractmethod
    async def generate_filter_settings(
        self,
        resume: str,
        user_filter_params: str | None = None,
    ) -> SuggestedUserFilterSettings:
        """Сгенерировать предположительные настройки фильтров.

        Возвращает только поля text/salary/currency, остальные остаются на усмотрение пользователя.
        """
        raise NotImplementedError

