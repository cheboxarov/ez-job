"""Роутер для WebSocket соединений."""

from __future__ import annotations

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from loguru import logger
from jose import jwt as jose_jwt
from jose.exceptions import JWTError, ExpiredSignatureError

from application.services.websocket_service import WebSocketService
from config import load_config
from presentation.dependencies import get_websocket_service

router = APIRouter()


async def get_user_id_from_token(token: str) -> str | None:
    """Извлечь user_id из JWT токена.
    
    Args:
        token: JWT токен.
        
    Returns:
        user_id из токена или None, если токен невалиден.
    """
    try:
        from infrastructure.auth.fastapi_users_setup import get_jwt_strategy
        
        strategy = get_jwt_strategy()
        
        # Обрабатываем token_audience: если это список, берем первый элемент
        # jose_jwt.decode ожидает строку или None для audience
        audience = strategy.token_audience
        if isinstance(audience, list):
            if len(audience) > 0:
                audience = audience[0]
            else:
                audience = None
        
        # Декодируем токен с проверкой подписи и audience
        decoded_token = jose_jwt.decode(
            token,
            strategy.secret,
            algorithms=[strategy.algorithm],
            audience=audience,
        )
        
        user_id = decoded_token.get("sub")
        return user_id
    except ExpiredSignatureError as exc:
        logger.warning(f"JWT токен истек: {exc}")
        return None
    except JWTError as exc:
        logger.warning(f"Ошибка при декодировании JWT токена: {exc}")
        return None
    except Exception as exc:
        logger.warning(f"Ошибка при декодировании JWT токена: {exc}")
        return None


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT токен для аутентификации"),
) -> None:
    """WebSocket endpoint для real-time событий.
    
    Args:
        websocket: WebSocket соединение.
        token: JWT токен для аутентификации (передаётся как query parameter).
    """
    # 1. Валидируем JWT токен
    user_id_str = await get_user_id_from_token(token)
    
    if not user_id_str:
        logger.warning("Невалидный JWT токен при подключении к WebSocket")
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    # 2. Извлекаем user_id
    from uuid import UUID
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        logger.warning(f"Невалидный user_id из токена: {user_id_str}")
        await websocket.close(code=1008, reason="Invalid user_id")
        return
    
    # 3. Получаем WebSocket Service
    websocket_service = await get_websocket_service()
    
    # 4. Передаём управление в websocket_service.handle_connection()
    try:
        await websocket_service.handle_connection(websocket, user_id)
    except WebSocketDisconnect:
        logger.info(f"WebSocket соединение закрыто клиентом для пользователя {user_id}")
    except Exception as exc:
        logger.error(
            f"Ошибка при обработке WebSocket соединения для пользователя {user_id}: {exc}",
            exc_info=True,
        )
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except Exception:
            pass
