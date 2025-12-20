"""DTO для запроса HH auth data."""

from __future__ import annotations

from typing import Dict

from pydantic import BaseModel, Field, field_validator


class HhAuthRequest(BaseModel):
    """DTO для сохранения HH auth data.

    Оба поля обязательны и должны быть валидными JSON-объектами (dict[str, str]).
    """

    headers: Dict[str, str] = Field(
        ...,
        description="HH API headers в формате JSON (ключ-значение, оба строки)",
    )
    cookies: Dict[str, str] = Field(
        ...,
        description="HH API cookies в формате JSON (ключ-значение, оба строки)",
    )

    @field_validator("headers", "cookies")
    @classmethod
    def validate_dict_string_values(cls, v: Dict[str, str]) -> Dict[str, str]:
        """Проверяет, что все значения в словаре - строки.

        Args:
            v: Словарь для валидации.

        Returns:
            Валидированный словарь.

        Raises:
            ValueError: Если найдено не-строковое значение.
        """
        for key, value in v.items():
            if not isinstance(value, str):
                raise ValueError(
                    f"Все значения должны быть строками. Ключ '{key}' имеет тип {type(value).__name__}"
                )
        return v
