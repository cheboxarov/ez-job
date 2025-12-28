"""Роутер для работы с Telegram уведомлениями."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from config import AppConfig
from domain.interfaces.telegram_bot_port import TelegramBotPort
from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from domain.use_cases.generate_telegram_link_token import (
    GenerateTelegramLinkTokenUseCase,
)
from domain.use_cases.get_telegram_settings import GetTelegramSettingsUseCase
from domain.use_cases.link_telegram_account import LinkTelegramAccountUseCase
from domain.use_cases.send_test_telegram_notification import (
    SendTestTelegramNotificationUseCase,
)
from domain.use_cases.unlink_telegram_account import UnlinkTelegramAccountUseCase
from domain.use_cases.update_telegram_notification_settings import (
    UpdateTelegramNotificationSettingsUseCase,
)
from infrastructure.auth.fastapi_users_setup import get_current_active_user
from infrastructure.database.models.user_model import UserModel
from presentation.dependencies import get_config, get_unit_of_work, get_telegram_bot
from presentation.dto.telegram_request import (
    LinkTelegramAccountRequest,
    UpdateTelegramNotificationSettingsRequest,
)
from presentation.dto.telegram_response import (
    GenerateTelegramLinkTokenResponse,
    SendTestNotificationResponse,
    TelegramNotificationSettingsResponse,
)

router = APIRouter(prefix="/api/telegram", tags=["telegram"])


@router.get("/settings", response_model=TelegramNotificationSettingsResponse)
async def get_telegram_settings(
    current_user: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
) -> TelegramNotificationSettingsResponse:
    """Получить настройки Telegram уведомлений текущего пользователя.

    Args:
        current_user: Текущий авторизованный пользователь.
        unit_of_work: UnitOfWork для работы с БД.

    Returns:
        Настройки Telegram уведомлений.
    """
    try:
        get_settings_uc = GetTelegramSettingsUseCase(
            settings_repository=unit_of_work.telegram_notification_settings_repository
        )
        settings = await get_settings_uc.execute(current_user.id)
        return TelegramNotificationSettingsResponse.from_entity(settings)
    except Exception as exc:
        logger.error(
            f"Ошибка при получении настроек Telegram для user_id={current_user.id}: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при получении настроек"
        ) from exc


@router.post("/link-token", response_model=GenerateTelegramLinkTokenResponse)
async def generate_link_token(
    current_user: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
    config: AppConfig = Depends(get_config),
) -> GenerateTelegramLinkTokenResponse:
    """Сгенерировать токен и ссылку для привязки Telegram аккаунта.

    Args:
        current_user: Текущий авторизованный пользователь.
        unit_of_work: UnitOfWork для работы с БД.
        config: Конфигурация приложения.

    Returns:
        Ссылка для привязки и время истечения токена.
    """
    try:
        generate_token_uc = GenerateTelegramLinkTokenUseCase(
            token_repository=unit_of_work.telegram_link_token_repository,
            token_ttl_seconds=config.telegram.link_token_ttl_seconds,
        )
        token = await generate_token_uc.execute(current_user.id)
        
        # Генерируем ссылку на бота (всегда, если bot_username задан)
        if not config.telegram.bot_username:
            raise HTTPException(
                status_code=500, 
                detail="Telegram bot username не настроен. Обратитесь к администратору."
            )
        
        link = f"https://t.me/{config.telegram.bot_username}?start={token}"
        
        # Вычисляем expires_at
        from datetime import datetime, timedelta, timezone
        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=config.telegram.link_token_ttl_seconds
        )
        
        return GenerateTelegramLinkTokenResponse(link=link, expires_at=expires_at)
    except Exception as exc:
        logger.error(
            f"Ошибка при генерации токена привязки для user_id={current_user.id}: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при генерации токена"
        ) from exc


@router.post("/link", response_model=TelegramNotificationSettingsResponse)
async def link_telegram_account(
    request: LinkTelegramAccountRequest,
    current_user: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
) -> TelegramNotificationSettingsResponse:
    """Привязать Telegram аккаунт к текущему пользователю.

    Args:
        request: Данные для привязки (токен, chat_id, username).
        current_user: Текущий авторизованный пользователь.
        unit_of_work: UnitOfWork для работы с БД.

    Returns:
        Обновленные настройки Telegram уведомлений.

    Raises:
        HTTPException: 400 если токен невалиден или истек.
    """
    try:
        link_account_uc = LinkTelegramAccountUseCase(
            token_repository=unit_of_work.telegram_link_token_repository,
            settings_repository=unit_of_work.telegram_notification_settings_repository,
        )
        settings = await link_account_uc.execute(
            token=request.token,
            telegram_chat_id=request.telegram_chat_id,
            telegram_username=request.telegram_username,
        )
        return TelegramNotificationSettingsResponse.from_entity(settings)
    except ValueError as exc:
        logger.warning(
            f"Ошибка валидации при привязке Telegram для user_id={current_user.id}: {exc}"
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(
            f"Ошибка при привязке Telegram для user_id={current_user.id}: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при привязке аккаунта"
        ) from exc


@router.post("/unlink")
async def unlink_telegram_account(
    current_user: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
) -> dict[str, str]:
    """Отвязать Telegram аккаунт от текущего пользователя.

    Args:
        current_user: Текущий авторизованный пользователь.
        unit_of_work: UnitOfWork для работы с БД.

    Returns:
        Сообщение об успешной отвязке.
    """
    try:
        unlink_account_uc = UnlinkTelegramAccountUseCase(
            settings_repository=unit_of_work.telegram_notification_settings_repository
        )
        await unlink_account_uc.execute(current_user.id)
        return {"message": "Telegram аккаунт успешно отвязан"}
    except Exception as exc:
        logger.error(
            f"Ошибка при отвязке Telegram для user_id={current_user.id}: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при отвязке аккаунта"
        ) from exc


@router.put("/settings", response_model=TelegramNotificationSettingsResponse)
async def update_telegram_settings(
    request: UpdateTelegramNotificationSettingsRequest,
    current_user: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
) -> TelegramNotificationSettingsResponse:
    """Обновить настройки Telegram уведомлений.

    Args:
        request: Новые настройки уведомлений.
        current_user: Текущий авторизованный пользователь.
        unit_of_work: UnitOfWork для работы с БД.

    Returns:
        Обновленные настройки Telegram уведомлений.

    Raises:
        HTTPException: 400 если настройки не найдены или аккаунт не привязан.
    """
    try:
        update_settings_uc = UpdateTelegramNotificationSettingsUseCase(
            settings_repository=unit_of_work.telegram_notification_settings_repository
        )
        settings = await update_settings_uc.execute(
            user_id=current_user.id,
            is_enabled=request.is_enabled,
            notify_call_request=request.notify_call_request,
            notify_external_action=request.notify_external_action,
            notify_question_answered=request.notify_question_answered,
            notify_message_suggestion=request.notify_message_suggestion,
            notify_vacancy_response=request.notify_vacancy_response,
        )
        return TelegramNotificationSettingsResponse.from_entity(settings)
    except ValueError as exc:
        logger.warning(
            f"Ошибка валидации при обновлении настроек Telegram для user_id={current_user.id}: {exc}"
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(
            f"Ошибка при обновлении настроек Telegram для user_id={current_user.id}: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при обновлении настроек"
        ) from exc


@router.post("/test-notification", response_model=SendTestNotificationResponse)
async def send_test_notification(
    current_user: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
    telegram_bot: TelegramBotPort = Depends(get_telegram_bot),
) -> SendTestNotificationResponse:
    """Отправить тестовое уведомление в Telegram.

    Args:
        current_user: Текущий авторизованный пользователь.
        unit_of_work: UnitOfWork для работы с БД.
        telegram_bot: Telegram бот для отправки уведомлений.

    Returns:
        Результат отправки тестового уведомления.

    Raises:
        HTTPException: 400 если Telegram аккаунт не привязан.
    """
    try:
        send_test_uc = SendTestTelegramNotificationUseCase(
            settings_repository=unit_of_work.telegram_notification_settings_repository,
            telegram_bot=telegram_bot,
        )
        success = await send_test_uc.execute(current_user.id)
        return SendTestNotificationResponse(success=success)
    except ValueError as exc:
        logger.warning(
            f"Ошибка валидации при отправке тестового уведомления для user_id={current_user.id}: {exc}"
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(
            f"Ошибка при отправке тестового уведомления для user_id={current_user.id}: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при отправке тестового уведомления"
        ) from exc
