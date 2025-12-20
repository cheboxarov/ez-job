"""Роутер для работы с HH auth data пользователя."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from infrastructure.auth.fastapi_users_setup import get_current_active_user
from infrastructure.database.models.user_model import UserModel
from presentation.dependencies import get_unit_of_work
from presentation.dto.hh_auth_request import HhAuthRequest
from presentation.dto.hh_auth_response import HhAuthResponse

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
