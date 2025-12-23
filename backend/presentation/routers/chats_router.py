"""Роутер для работы с чатами."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from domain.use_cases.fetch_chat_detail import FetchChatDetailUseCase
from domain.use_cases.fetch_user_chats import FetchUserChatsUseCase
from domain.use_cases.send_chat_message import SendChatMessageUseCase
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase
from infrastructure.auth.fastapi_users_setup import get_current_active_user
from infrastructure.database.models.user_model import UserModel
from presentation.dependencies import (
    get_cookies,
    get_fetch_chat_detail_uc,
    get_fetch_user_chats_uc,
    get_headers,
    get_send_chat_message_uc,
    get_unit_of_work,
)
from presentation.dto.chat_request import SendChatMessageRequest
from presentation.dto.chat_response import ChatDetailedResponse, ChatListResponse, SendChatMessageResponse

router = APIRouter(prefix="/api/chats", tags=["chats"])


@router.get("", response_model=ChatListResponse)
async def list_chats(
    current_user: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
    headers: dict[str, str] = Depends(get_headers),
    cookies: dict[str, str] = Depends(get_cookies),
    fetch_user_chats_uc: FetchUserChatsUseCase = Depends(get_fetch_user_chats_uc),
) -> ChatListResponse:
    """Получить список непрочитанных чатов пользователя.

    Returns:
        Список непрочитанных чатов с информацией для отображения.
    """
    try:
        # Создаем use case для обновления cookies
        update_cookies_uc = UpdateUserHhAuthCookiesUseCase(
            unit_of_work.user_hh_auth_data_repository
        )

        # Получаем список непрочитанных чатов
        chat_list = await fetch_user_chats_uc.execute(
            headers=headers,
            cookies=cookies,
            user_id=current_user.id,
            update_cookies_uc=update_cookies_uc,
        )

        return ChatListResponse.from_entity(chat_list)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - обёртка ошибок HTTP
        logger.error(f"Ошибка при получении списка чатов: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка при получении списка чатов",
        ) from exc


@router.get("/{chat_id}", response_model=ChatDetailedResponse)
async def get_chat(
    chat_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
    headers: dict[str, str] = Depends(get_headers),
    cookies: dict[str, str] = Depends(get_cookies),
    fetch_chat_detail_uc: FetchChatDetailUseCase = Depends(get_fetch_chat_detail_uc),
) -> ChatDetailedResponse:
    """Получить детальную информацию о чате с сообщениями.

    Args:
        chat_id: ID чата для получения детальной информации.

    Returns:
        Детальная информация о чате с сообщениями.

    Raises:
        HTTPException: 404 если чат не найден.
    """
    try:
        # Создаем use case для обновления cookies
        update_cookies_uc = UpdateUserHhAuthCookiesUseCase(
            unit_of_work.user_hh_auth_data_repository
        )

        # Получаем детальную информацию о чате
        chat = await fetch_chat_detail_uc.execute(
            chat_id=chat_id,
            headers=headers,
            cookies=cookies,
            user_id=current_user.id,
            update_cookies_uc=update_cookies_uc,
        )

        if chat is None:
            raise HTTPException(
                status_code=404,
                detail=f"Чат с ID {chat_id} не найден",
            )

        return ChatDetailedResponse.from_entity(chat)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - обёртка ошибок HTTP
        logger.error(f"Ошибка при получении чата {chat_id}: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка при получении чата {chat_id}",
        ) from exc


@router.post("/{chat_id}/send", response_model=SendChatMessageResponse)
async def send_chat_message(
    chat_id: int,
    request: SendChatMessageRequest,
    current_user: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
    headers: dict[str, str] = Depends(get_headers),
    cookies: dict[str, str] = Depends(get_cookies),
    send_chat_message_uc: SendChatMessageUseCase = Depends(get_send_chat_message_uc),
) -> SendChatMessageResponse:
    """Отправить сообщение в чат.

    Args:
        chat_id: ID чата для отправки сообщения.
        request: Запрос с текстом сообщения и опциональными параметрами.

    Returns:
        Результат отправки сообщения.

    Raises:
        HTTPException: 400 если текст сообщения пустой, 500 при внутренней ошибке.
    """
    try:
        # Создаем use case для обновления cookies
        update_cookies_uc = UpdateUserHhAuthCookiesUseCase(
            unit_of_work.user_hh_auth_data_repository
        )

        # Отправляем сообщение
        result = await send_chat_message_uc.execute(
            chat_id=chat_id,
            text=request.text,
            headers=headers,
            cookies=cookies,
            user_id=current_user.id,
            update_cookies_uc=update_cookies_uc,
            idempotency_key=request.idempotency_key,
            hhtm_source=request.hhtm_source,
            hhtm_source_label=request.hhtm_source_label,
        )

        return SendChatMessageResponse(success=True, data=result)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - обёртка ошибок HTTP
        logger.error(f"Ошибка при отправке сообщения в чат {chat_id}: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка при отправке сообщения в чат {chat_id}",
        ) from exc

