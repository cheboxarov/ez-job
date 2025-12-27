"""DTO для запросов OTP авторизации в HH."""

from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class CaptchaPayload(BaseModel):
    """Данные для решения капчи HH."""

    captchaText: str = Field(..., description="Текст, введённый пользователем с картинки капчи")
    captchaKey: str = Field(..., description="Ключ капчи, полученный с /captcha?lang=RU")
    captchaState: str = Field(..., description="captchaState из ответа otp_generate.hhcaptcha.captchaState")


class GenerateOtpRequest(BaseModel):
    """DTO для запроса OTP кода."""

    phone: str = Field(..., description="Номер телефона в формате +7XXXXXXXXXX")
    cookies: Optional[Dict[str, str]] = Field(
        default=None,
        description="Промежуточные cookies HH (если не переданы, бэкенд получит их сам)",
    )
    captcha: Optional[CaptchaPayload] = Field(
        default=None,
        description="Опциональные данные капчи HH (captchaText/captchaKey/captchaState)",
    )


class GenerateOtpResponse(BaseModel):
    """DTO для ответа на запрос OTP кода."""

    result: Dict[str, Any] = Field(..., description="Результат запроса от HH API")
    cookies: Dict[str, str] = Field(..., description="Промежуточные cookies для следующего шага")


class LoginByCodeRequest(BaseModel):
    """DTO для входа по OTP коду."""

    phone: str = Field(..., description="Номер телефона в формате +7XXXXXXXXXX")
    code: str = Field(..., description="OTP код из SMS")
    cookies: Dict[str, str] = Field(..., description="Промежуточные cookies из предыдущего шага")


class CaptchaKeyRequest(BaseModel):
    """DTO для запроса ключа капчи HH."""

    cookies: Dict[str, str] = Field(..., description="Текущие cookies HH для captcha запроса")
    lang: str = Field("RU", description="Язык капчи (по умолчанию RU)")


class CaptchaKeyResponse(BaseModel):
    """DTO с ключом капчи HH."""

    captchaKey: str = Field(..., description="Ключ капчи (UUID) из /captcha")
    cookies: Dict[str, str] = Field(..., description="Обновлённые cookies после запроса капчи")


class CaptchaPictureRequest(BaseModel):
    """DTO для запроса картинки капчи HH."""

    captchaKey: str = Field(..., description="Ключ капчи (UUID) из /captcha")
    cookies: Dict[str, str] = Field(..., description="Текущие cookies HH для запроса картинки")


class CaptchaPictureResponse(BaseModel):
    """DTO с картинкой капчи HH в base64."""

    contentType: str = Field(..., description="MIME-тип картинки капчи (например image/png)")
    imageBase64: str = Field(..., description="Картинка капчи в base64")
    cookies: Dict[str, str] = Field(..., description="Обновлённые cookies после запроса картинки")

