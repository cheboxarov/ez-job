from __future__ import annotations
from uuid import UUID

from domain.entities.suggested_user_filter_settings import SuggestedUserFilterSettings
from domain.interfaces.filter_settings_generator_service_port import (
    FilterSettingsGeneratorServicePort,
)
from domain.exceptions.agent_exceptions import AgentParseError
from loguru import logger


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
        user_id: UUID | None = None,
    ) -> SuggestedUserFilterSettings:
        try:
            return await self._generator_service.generate_filter_settings(
                resume=resume,
                user_filter_params=user_filter_params,
                user_id=user_id,
            )
        except AgentParseError as exc:
            logger.error(
                f"Ошибка парсинга ответа агента при генерации настроек фильтров: {exc}",
                exc_info=True,
            )
            return SuggestedUserFilterSettings()


