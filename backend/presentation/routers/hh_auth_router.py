"""Роутер для работы с HH auth data пользователя."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from infrastructure.auth.fastapi_users_setup import auth_backend
from infrastructure.database.models.user_model import UserModel
from infrastructure.database.session import create_session_factory
from presentation.dependencies import get_hh_auth_service, get_unit_of_work
from presentation.dto.hh_auth_otp_request import (
    CaptchaKeyRequest,
    CaptchaKeyResponse,
    CaptchaPictureRequest,
    CaptchaPictureResponse,
    GenerateOtpRequest,
    GenerateOtpResponse,
    LoginByCodeRequest,
)
from presentation.dto.hh_auth_response import HhAuthResponse
from config import load_config
from fastapi_users.authentication import JWTStrategy
from fastapi_users.jwt import generate_jwt
from datetime import timedelta, timezone, datetime
from typing import Any, Dict
import json
from pathlib import Path
from domain.interfaces.hh_auth_service_port import HhAuthServicePort

router = APIRouter(prefix="/api/hh-auth", tags=["hh-auth"])


@router.get("", response_model=HhAuthResponse)
async def get_hh_auth() -> HhAuthResponse:
    """[DEPRECATED] Эндпоинт больше не используется и всегда возвращает 404."""
    raise HTTPException(status_code=404, detail="HH auth data endpoint is deprecated")


@router.put("", response_model=HhAuthResponse)
async def update_hh_auth() -> HhAuthResponse:
    """[DEPRECATED] Эндпоинт больше не используется и всегда возвращает 404."""
    raise HTTPException(status_code=404, detail="HH auth data endpoint is deprecated")


@router.post("/generate-otp", response_model=GenerateOtpResponse)
async def generate_otp(
    request: GenerateOtpRequest,
    hh_auth_service: HhAuthServicePort = Depends(get_hh_auth_service),
) -> GenerateOtpResponse:
    """Запросить OTP код на телефон.

    Args:
        request: Данные запроса (номер телефона).
        hh_auth_service: Сервис авторизации HH.

    Returns:
        Результат запроса и промежуточные cookies.

    Raises:
        HTTPException: 400 при ошибках валидации, 500 при внутренних ошибках.
    """
    try:
        # cookies и captcha опциональны: если cookies нет, сервис сам получит initial cookies
        captcha_payload = (
            {
                "captchaText": request.captcha.captchaText,
                "captchaKey": request.captcha.captchaKey,
                "captchaState": request.captcha.captchaState,
            }
            if request.captcha is not None
            else None
        )
        result, cookies = await hh_auth_service.generate_otp(
            phone=request.phone,
            cookies=request.cookies,
            captcha=captcha_payload,
        )
        return GenerateOtpResponse(result=result, cookies=cookies)
    except ValueError as exc:
        logger.error(f"Ошибка валидации при запросе OTP: {exc}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(
            f"Внутренняя ошибка при запросе OTP кода: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при запросе OTP кода"
        ) from exc


@router.post("/captcha/key", response_model=CaptchaKeyResponse)
async def get_captcha_key(
    request: CaptchaKeyRequest,
    hh_auth_service: HhAuthServicePort = Depends(get_hh_auth_service),
) -> CaptchaKeyResponse:
    """Получить ключ капчи HH (обёртка над /captcha?lang=RU)."""
    try:
        result, cookies = await hh_auth_service.get_captcha_key(
            cookies=request.cookies,
            lang=request.lang,
        )
        captcha_key = result.get("key")
        if not captcha_key:
            raise HTTPException(status_code=500, detail="HH не вернул ключ капчи")
        return CaptchaKeyResponse(captchaKey=captcha_key, cookies=cookies)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            f"Внутренняя ошибка при запросе ключа капчи: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при запросе ключа капчи"
        ) from exc


@router.post("/captcha/picture", response_model=CaptchaPictureResponse)
async def get_captcha_picture(
    request: CaptchaPictureRequest,
    hh_auth_service: HhAuthServicePort = Depends(get_hh_auth_service),
) -> CaptchaPictureResponse:
    """Получить картинку капчи HH в base64."""
    try:
        result, cookies = await hh_auth_service.get_captcha_picture(
            cookies=request.cookies,
            captcha_key=request.captchaKey,
        )
        content_type = result.get("content_type") or "image/png"
        image_base64 = result.get("image_base64")
        if not image_base64:
            raise HTTPException(status_code=500, detail="HH не вернул картинку капчи")
        return CaptchaPictureResponse(
            contentType=content_type,
            imageBase64=image_base64,
            cookies=cookies,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            f"Внутренняя ошибка при запросе картинки капчи: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при запросе картинки капчи"
        ) from exc


def _get_jwt_strategy() -> JWTStrategy:
    """Получить стратегию JWT так же, как в fastapi_users_setup."""
    config = load_config()
    # Секрет и время жизни должны совпадать с настройками auth_backend/JWTStrategy
    # В fastapi_users_setup сейчас SECRET и lifetime_seconds заданы жёстко.
    return JWTStrategy(secret="SECRET", lifetime_seconds=7200000)


def _create_access_token(user: UserModel) -> Dict[str, Any]:
    """Сгенерировать access_token в формате LoginResponse."""
    strategy = _get_jwt_strategy()
    now = datetime.now(timezone.utc)
    exp = now + timedelta(seconds=strategy.lifetime_seconds)
    data = {"sub": str(user.id), "aud": strategy.token_audience}
    token = generate_jwt(
        data,
        strategy.secret,
        strategy.lifetime_seconds,
        algorithm=strategy.algorithm,
    )
    return {"access_token": token, "token_type": "bearer"}


# region agent log
def _debug_log(hypothesis_id: str, location: str, message: str, data: Dict[str, Any]) -> None:
    """Локальный логгер для отладки HH login-by-code в debug-mode."""
    try:
        log_path = Path("/Users/apple/dev/hh/.cursor/debug.log")
        payload = {
            "sessionId": "hh-auth-debug",
            "runId": "login-by-code",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
        }
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        # Логгирование не должно ломать основной флоу
        logger.debug("debug_log failed at %s", location)
# endregion


@router.post("/login-by-code")
async def login_by_code(
    request: LoginByCodeRequest,
    hh_auth_service: HhAuthServicePort = Depends(get_hh_auth_service),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
) -> Dict[str, Any]:
    """Войти по OTP коду в HH, привязать/создать пользователя и выдать JWT токен.

    Args:
        request: Данные запроса (номер телефона, код, промежуточные cookies).
        unit_of_work: UnitOfWork для возможной инициализации зависимостей (пока не используется напрямую).
        hh_auth_service: Сервис авторизации HH.

    Returns:
        LoginResponse‑совместный словарь: {\"access_token\", \"token_type\"}.

    Raises:
        HTTPException: 400 при ошибках валидации, 500 при внутренних ошибках.
    """
    try:
        # 1. Входим в HH и получаем финальные headers/cookies
        headers, final_cookies = await hh_auth_service.login_by_code(
            phone=request.phone,
            code=request.code,
            cookies=request.cookies,
        )
        
        # 2. Достаём hh_user_id из cookies.
        # Используем cookie "hhul" (user login), а не "hhuid" (device/session id),
        # чтобы различать разные аккаунты HH в одном браузере.
        hh_user_id = request.phone.replace("+", "")
        _debug_log(
            hypothesis_id="H1",
            location="hh_auth_router.login_by_code:after_hh_login",
            message="HH login completed",
            data={
                "phone": request.phone,
                "has_hhuid": bool(hh_user_id),
                "cookie_keys": list(final_cookies.keys()),
                "hhuid_cookie": final_cookies.get("hhuid"),
                "hhul_cookie": final_cookies.get("hhul"),
            },
        )
        if not hh_user_id:
            raise HTTPException(
                status_code=400,
                detail="Не удалось определить hh_user_id из cookies (нет cookie 'hhul')",
            )

        # 3. Ищем/создаём пользователя в БД по hh_user_id
        config = load_config()
        session_factory = create_session_factory(config.database)

        from sqlalchemy import select

        async with session_factory() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.hh_user_id == hh_user_id)
            )
            user: UserModel | None = result.scalar_one_or_none()

            if user is None:
                # Создаём нового пользователя
                # Email и пароль технические, вход по паролю не используется
                synthetic_email = f"hh_{hh_user_id}@hh.ru"
                user = UserModel(
                    email=synthetic_email,
                    hashed_password="not_used",
                    is_active=True,
                    is_superuser=False,
                    is_verified=True,
                    resume_id=None,
                    area=None,
                    salary=None,
                    hh_user_id=hh_user_id,
                    hh_headers=headers,
                    hh_cookies=final_cookies,
                    phone=request.phone,
                )
                session.add(user)
                branch = "created"
            else:
                # Обновляем сессию и телефон
                user.hh_headers = headers
                user.hh_cookies = final_cookies
                # Телефон можем обновлять всегда, чтобы актуализировать
                user.phone = request.phone
                branch = "updated"

            await session.flush()
            await session.refresh(user)
            await session.commit()

        _debug_log(
            hypothesis_id="H2",
            location="hh_auth_router.login_by_code:after_user_persist",
            message="User linked to hhuid",
            data={
                "branch": branch,
                "user_id": str(user.id),
                "hh_user_id": hh_user_id,
            },
        )

        # 4. Генерируем JWT токен для пользователя
        token_payload = _create_access_token(user)
        return token_payload
    except ValueError as exc:
        logger.error(f"Ошибка валидации при входе по коду: {exc}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            f"Внутренняя ошибка при входе по OTP коду: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при входе по OTP коду"
        ) from exc


@router.delete("")
async def delete_hh_auth() -> dict[str, str]:
    """[DEPRECATED] Эндпоинт больше не используется и всегда возвращает 404."""
    raise HTTPException(status_code=404, detail="HH auth data endpoint is deprecated")
