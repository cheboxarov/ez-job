"""Роутер для работы с пользователями."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger

from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from presentation.dependencies import (
    get_current_user,
    get_unit_of_work,
)
from presentation.dto.user_request import UpdateUserRequest
from presentation.dto.user_response import UserResponse

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
) -> UserResponse:
    """Получить пользователя по ID."""
    try:
        user = await unit_of_work.standalone_user_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=404, detail=f"Пользователь с ID {user_id} не найден"
            )
        return UserResponse.from_entity(user)
    except Exception as exc:  # pragma: no cover - обёртка ошибок HTTP
        logger.error(f"Ошибка при получении пользователя: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при получении пользователя"
        ) from exc


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    request: UpdateUserRequest,
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
) -> UserResponse:
    """Обновить пользователя по ID.

    User теперь содержит только id, обновлять нечего.
    Оставлено для совместимости с API.
    """
    try:
        # Получаем существующего пользователя
        existing_user = await unit_of_work.standalone_user_repository.get_by_id(user_id)
        if existing_user is None:
            raise HTTPException(
                status_code=404, detail=f"Пользователь с ID {user_id} не найден"
            )

        # User теперь содержит только id, обновлять нечего
        return UserResponse.from_entity(existing_user)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - обёртка ошибок HTTP
        logger.error(
            f"Внутренняя ошибка при обновлении пользователя: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при обновлении пользователя"
        ) from exc


