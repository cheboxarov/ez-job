"""Роутер для работы с настройками автоматизации."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from domain.use_cases.get_user_automation_settings import GetUserAutomationSettingsUseCase
from domain.use_cases.update_user_automation_settings import (
    UpdateUserAutomationSettingsUseCase,
)
from infrastructure.auth.fastapi_users_setup import get_current_active_user
from infrastructure.database.models.user_model import UserModel
from presentation.dependencies import get_unit_of_work
from presentation.dto.automation_request import UpdateUserAutomationSettingsRequest
from presentation.dto.automation_response import UserAutomationSettingsResponse

router = APIRouter(prefix="/api/settings/automation", tags=["automation"])


@router.get("", response_model=UserAutomationSettingsResponse)
async def get_automation_settings(
    current_user: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
) -> UserAutomationSettingsResponse:
    """Получить настройки автоматизации текущего пользователя.

    Args:
        current_user: Текущий авторизованный пользователь.
        unit_of_work: UnitOfWork для работы с БД.

    Returns:
        Настройки автоматизации пользователя.
    """
    try:
        get_settings_uc = GetUserAutomationSettingsUseCase(
            settings_repository=unit_of_work.user_automation_settings_repository
        )
        settings = await get_settings_uc.execute(current_user.id)
        return UserAutomationSettingsResponse.from_entity(settings)
    except Exception as exc:
        logger.error(
            f"Ошибка при получении настроек автоматизации для user_id={current_user.id}: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при получении настроек"
        ) from exc


@router.put("", response_model=UserAutomationSettingsResponse)
async def update_automation_settings(
    request: UpdateUserAutomationSettingsRequest,
    current_user: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
) -> UserAutomationSettingsResponse:
    """Обновить настройки автоматизации пользователя.

    Args:
        request: Новые настройки автоматизации.
        current_user: Текущий авторизованный пользователь.
        unit_of_work: UnitOfWork для работы с БД.

    Returns:
        Обновленные настройки автоматизации пользователя.

    Raises:
        HTTPException: 400 если настройки не найдены.
    """
    try:
        update_settings_uc = UpdateUserAutomationSettingsUseCase(
            settings_repository=unit_of_work.user_automation_settings_repository
        )
        settings = await update_settings_uc.execute(
            user_id=current_user.id,
            auto_reply_to_questions_in_chats=request.auto_reply_to_questions_in_chats,
        )
        return UserAutomationSettingsResponse.from_entity(settings)
    except ValueError as exc:
        logger.warning(
            f"Ошибка валидации при обновлении настроек автоматизации для user_id={current_user.id}: {exc}"
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(
            f"Ошибка при обновлении настроек автоматизации для user_id={current_user.id}: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при обновлении настроек"
        ) from exc
