"""DTO для запросов OTP авторизации в HH."""

from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel, Field


class GenerateOtpRequest(BaseModel):
    """DTO для запроса OTP кода."""

    phone: str = Field(..., description="Номер телефона в формате +7XXXXXXXXXX")


class GenerateOtpResponse(BaseModel):
    """DTO для ответа на запрос OTP кода."""

    result: Dict[str, Any] = Field(..., description="Результат запроса от HH API")
    cookies: Dict[str, str] = Field(..., description="Промежуточные cookies для следующего шага")


class LoginByCodeRequest(BaseModel):
    """DTO для входа по OTP коду."""

    phone: str = Field(..., description="Номер телефона в формате +7XXXXXXXXXX")
    code: str = Field(..., description="OTP код из SMS")
    cookies: Dict[str, str] = Field(..., description="Промежуточные cookies из предыдущего шага")

