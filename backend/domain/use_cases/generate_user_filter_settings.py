from __future__ import annotations

from domain.entities.suggested_user_filter_settings import SuggestedUserFilterSettings
from domain.interfaces.filter_settings_generator_service_port import (
    FilterSettingsGeneratorServicePort,
)


class GenerateUserFilterSettingsUseCase:
    """Use case для генерации предложенных настроек фильтров пользователя."""

    def __init__(
        self,
        generator_service: FilterSettingsGeneratorServicePort,
    ) -> None:
        self._generator_service = generator_service

    async def execute(
        self,
        *,
        resume: str,
        user_filter_params: str | None = None,
    ) -> SuggestedUserFilterSettings:
        return await self._generator_service.generate_filter_settings(
            resume=resume,
            user_filter_params=user_filter_params,
        )


