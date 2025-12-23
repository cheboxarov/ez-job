"""Роутер для работы с действиями агента."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from uuid import UUID

from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from domain.interfaces.agent_action_service_port import AgentActionServicePort
from domain.use_cases.list_agent_actions import ListAgentActionsUseCase
from infrastructure.auth.fastapi_users_setup import get_current_active_user
from infrastructure.database.models.user_model import UserModel
from presentation.dependencies import (
    get_agent_action_service,
    get_list_agent_actions_uc,
    get_unit_of_work,
)
from presentation.dto.agent_action_response import (
    AgentActionResponse,
    AgentActionsListResponse,
    AgentActionsUnreadCountResponse,
)

router = APIRouter(prefix="/api/agent-actions", tags=["agent-actions"])


@router.get("", response_model=AgentActionsListResponse)
async def list_agent_actions(
    type: str | None = Query(None, description="Фильтр по типу действия"),
    entity_type: str | None = Query(None, description="Фильтр по типу сущности"),
    entity_id: int | None = Query(None, description="Фильтр по ID сущности"),
    current_user: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
    list_agent_actions_uc: ListAgentActionsUseCase = Depends(get_list_agent_actions_uc),
) -> AgentActionsListResponse:
    """Получить список действий агента с фильтрацией.

    Автоматически фильтрует по user_id текущего пользователя.

    Args:
        type: Фильтр по типу действия (например, "send_message", "create_event").
        entity_type: Фильтр по типу сущности (например, "hh_dialog").
        entity_id: Фильтр по ID сущности (например, ID диалога).
        current_user: Текущий авторизованный пользователь.
        unit_of_work: UnitOfWork для работы с БД.
        list_agent_actions_uc: Use case для получения списка действий.

    Returns:
        Список действий агента, отсортированный по created_at (desc).

    Raises:
        HTTPException: 500 при внутренней ошибке.
    """
    try:
        # Получаем действия с фильтрацией
        actions = await list_agent_actions_uc.execute(
            type=type,
            entity_type=entity_type,
            entity_id=entity_id,
            created_by=None,  # Не фильтруем по created_by в API
        )

        # Фильтруем по user_id текущего пользователя
        user_actions = [action for action in actions if action.user_id == current_user.id]

        # Преобразуем в DTO
        items = [AgentActionResponse.from_entity(action) for action in user_actions]

        return AgentActionsListResponse(items=items)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - обёртка ошибок HTTP
        logger.error(f"Ошибка при получении списка действий агента: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка при получении списка действий агента",
        ) from exc


@router.get("/unread/count", response_model=AgentActionsUnreadCountResponse)
async def get_unread_agent_actions_count(
    current_user: UserModel = Depends(get_current_active_user),
    agent_action_service: AgentActionServicePort = Depends(get_agent_action_service),
) -> AgentActionsUnreadCountResponse:
    """Получить количество непрочитанных действий агента для текущего пользователя."""
    try:
        unread_count = await agent_action_service.get_unread_count(current_user.id)
        return AgentActionsUnreadCountResponse(unread_count=unread_count)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            f"Ошибка при получении количества непрочитанных действий агента: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка при получении количества непрочитанных действий агента",
        ) from exc


@router.post("/read-all")
async def mark_all_agent_actions_as_read(
    current_user: UserModel = Depends(get_current_active_user),
    agent_action_service: AgentActionServicePort = Depends(get_agent_action_service),
) -> None:
    """Пометить все действия агента для текущего пользователя как прочитанные."""
    try:
        await agent_action_service.mark_all_as_read(current_user.id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            f"Ошибка при пометке действий агента как прочитанных: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка при пометке действий агента как прочитанных",
        ) from exc

