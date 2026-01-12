"""Роутер для WebSocket соединений редактирования резюме."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from loguru import logger
from jose import jwt as jose_jwt
from jose.exceptions import JWTError, ExpiredSignatureError

from application.services.resume_edit_websocket_handler import ResumeEditWebSocketHandler
from presentation.routers.websocket_router import get_user_id_from_token

router = APIRouter()


async def get_resume_edit_websocket_handler() -> ResumeEditWebSocketHandler:
    """Получить обработчик WebSocket для редактирования резюме.

    Returns:
        ResumeEditWebSocketHandler.
    """
    from application.services.resume_edit_service import ResumeEditService
    from application.factories.database_factory import create_unit_of_work
    from config import load_config
    from infrastructure.agents.resume_edit.deepagents.resume_edit_deep_agent import (
        ResumeEditDeepAgentAdapter,
        create_resume_edit_deep_agent,
    )

    config = load_config()
    unit_of_work = create_unit_of_work(config.database)
    deep_agent = create_resume_edit_deep_agent(config.openai, unit_of_work=unit_of_work)
    agent_adapter = ResumeEditDeepAgentAdapter(
        config.openai, agent=deep_agent, unit_of_work=unit_of_work
    )
    service = ResumeEditService(unit_of_work, agent_adapter)
    return ResumeEditWebSocketHandler(service, deep_agent, unit_of_work)


@router.websocket("/ws/resume-edit/{resume_id}")
async def resume_edit_websocket_endpoint(
    websocket: WebSocket,
    resume_id: UUID,
    token: str = Query(..., description="JWT токен для аутентификации"),
) -> None:
    """WebSocket endpoint для редактирования резюме в реальном времени.

    Args:
        websocket: WebSocket соединение.
        resume_id: UUID резюме для редактирования.
        token: JWT токен для аутентификации (передаётся как query parameter).
    """
    # 1. Валидируем JWT токен
    user_id_str = await get_user_id_from_token(token)

    if not user_id_str:
        logger.warning("Невалидный JWT токен при подключении к WebSocket редактирования резюме")
        await websocket.close(code=1008, reason="Invalid token")
        return

    # 2. Извлекаем user_id
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        logger.warning(f"Невалидный user_id из токена: {user_id_str}")
        await websocket.close(code=1008, reason="Invalid user_id")
        return

    # 3. Получаем обработчик WebSocket
    handler = await get_resume_edit_websocket_handler()

    # 4. Передаём управление в handler
    try:
        await handler.handle_connection(websocket, resume_id, user_id)
    except WebSocketDisconnect:
        logger.info(
            f"WebSocket соединение для редактирования резюме закрыто клиентом: "
            f"resume_id={resume_id}, user_id={user_id}"
        )
    except Exception as exc:
        logger.error(
            f"Ошибка при обработке WebSocket соединения для редактирования резюме: "
            f"resume_id={resume_id}, user_id={user_id}, error={exc}",
            exc_info=True,
        )
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except Exception as close_exc:
            logger.warning(
                f"Не удалось закрыть WebSocket соединение: "
                f"resume_id={resume_id}, user_id={user_id}, error={close_exc}"
            )
