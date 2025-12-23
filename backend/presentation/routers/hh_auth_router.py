"""Роутер для работы с HH auth data пользователя."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from infrastructure.auth.fastapi_users_setup import get_current_active_user
from infrastructure.database.models.user_model import UserModel
from presentation.dependencies import get_hh_auth_service, get_unit_of_work
from presentation.dto.hh_auth_request import HhAuthRequest
from presentation.dto.hh_auth_otp_request import (
    GenerateOtpRequest,
    GenerateOtpResponse,
    LoginByCodeRequest,
)
from presentation.dto.hh_auth_response import HhAuthResponse
from domain.interfaces.hh_auth_service_port import HhAuthServicePort

router = APIRouter(prefix="/api/hh-auth", tags=["hh-auth"])


@router.get("", response_model=HhAuthResponse)
async def get_hh_auth(
    current_user: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
) -> HhAuthResponse:
    """Получить HH auth data текущего пользователя.

    Args:
        current_user: Текущий авторизованный пользователь.
        unit_of_work: UnitOfWork для работы с БД.

    Returns:
        HH auth data пользователя.

    Raises:
        HTTPException: 404 если данные не найдены.
    """
    try:
        auth_data = await unit_of_work.user_hh_auth_data_repository.get_by_user_id(
            current_user.id
        )
        if auth_data is None:
            raise HTTPException(
                status_code=404, detail="HH auth data not set"
            )
        return HhAuthResponse.from_entity(auth_data)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            f"Ошибка при получении HH auth data: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при получении HH auth data"
        ) from exc


@router.put("", response_model=HhAuthResponse)
async def update_hh_auth(
    request: HhAuthRequest,
    current_user: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
) -> HhAuthResponse:
    """Сохранить или обновить HH auth data текущего пользователя.

    Args:
        request: Данные для сохранения (headers и cookies).
        current_user: Текущий авторизованный пользователь.
        unit_of_work: UnitOfWork для работы с БД.

    Returns:
        Сохраненные HH auth data пользователя.

    Raises:
        HTTPException: 400 при ошибках валидации, 500 при внутренних ошибках.
    """
    try:
        auth_data = await unit_of_work.user_hh_auth_data_repository.upsert(
            user_id=current_user.id,
            headers=request.headers,
            cookies=request.cookies,
        )
        await unit_of_work.commit()
        return HhAuthResponse.from_entity(auth_data)
    except ValueError as exc:
        logger.error(f"Ошибка валидации HH auth data: {exc}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(
            f"Внутренняя ошибка при сохранении HH auth data: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при сохранении HH auth data"
        ) from exc


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
        result, cookies = await hh_auth_service.generate_otp(request.phone)
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


@router.post("/login-by-code", response_model=HhAuthResponse)
async def login_by_code(
    request: LoginByCodeRequest,
    current_user: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
    hh_auth_service: HhAuthServicePort = Depends(get_hh_auth_service),
) -> HhAuthResponse:
    """Войти по OTP коду и сохранить cookies в БД.

    Args:
        request: Данные запроса (номер телефона, код, промежуточные cookies).
        current_user: Текущий авторизованный пользователь.
        unit_of_work: UnitOfWork для работы с БД.
        hh_auth_service: Сервис авторизации HH.

    Returns:
        Сохраненные HH auth data пользователя.

    Raises:
        HTTPException: 400 при ошибках валидации, 500 при внутренних ошибках.
    """
    try:
        cookies = await hh_auth_service.login_by_code(
            user_id=current_user.id,
            phone=request.phone,
            code=request.code,
            cookies=request.cookies,
            unit_of_work=unit_of_work,
        )
        
        # Получаем сохраненные данные для ответа
        auth_data = await unit_of_work.user_hh_auth_data_repository.get_by_user_id(
            current_user.id
        )
        if auth_data is None:
            raise HTTPException(
                status_code=500, detail="Не удалось получить сохраненные auth data"
            )
        
        return HhAuthResponse.from_entity(auth_data)
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
async def delete_hh_auth(
    current_user: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
) -> dict[str, str]:
    """Удалить HH auth data текущего пользователя (выйти из HH).

    Args:
        current_user: Текущий авторизованный пользователь.
        unit_of_work: UnitOfWork для работы с БД.

    Returns:
        Сообщение об успешном удалении.

    Raises:
        HTTPException: 500 при внутренних ошибках.
    """
    try:
        await unit_of_work.user_hh_auth_data_repository.delete(current_user.id)
        await unit_of_work.commit()
        return {"message": "HH auth data успешно удалены"}
    except Exception as exc:
        logger.error(
            f"Ошибка при удалении HH auth data: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при удалении HH auth data"
        ) from exc
