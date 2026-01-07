"""Сервис приложения для генерации предложенных настроек фильтров пользователя."""

from __future__ import annotations

from domain.entities.resume import Resume
from domain.entities.suggested_user_filter_settings import SuggestedUserFilterSettings
from domain.use_cases.generate_user_filter_settings import GenerateUserFilterSettingsUseCase


class FilterSettingsGenerationService:
    """Фасад над use case генерации предложенных настроек фильтров."""

    def __init__(self, use_case: GenerateUserFilterSettingsUseCase) -> None:
        self._use_case = use_case

    async def generate_for_resume(self, resume: Resume) -> SuggestedUserFilterSettings:
        """Сгенерировать настройки фильтров на основе резюме.

        Требует, чтобы у резюме был заполнен content.
        """
        if not resume.content or not resume.content.strip():
            raise ValueError("content не заполнен в резюме")

        return await self._use_case.execute(
            resume=resume.content,
            user_filter_params=resume.user_parameters,
            user_id=resume.user_id,
        )


