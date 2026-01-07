"""Роутер для работы с подписками."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from domain.use_cases.check_and_update_subscription import (
    CheckAndUpdateSubscriptionUseCase,
)
from domain.use_cases.change_user_subscription import (
    ChangeUserSubscriptionUseCase,
)
from infrastructure.auth.fastapi_users_setup import get_current_active_user
from infrastructure.database.models.user_model import UserModel
from presentation.dependencies import get_unit_of_work
from presentation.dto.subscription_request import ChangePlanRequest
from presentation.dto.subscription_response import (
    DailyResponsesResponse,
    PlansListResponse,
    SubscriptionPlanResponse,
    UserSubscriptionResponse,
)

router = APIRouter(prefix="/api/subscription", tags=["subscription"])


@router.get("/my-plan", response_model=UserSubscriptionResponse)
async def get_my_subscription_plan(
    current_user: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
) -> UserSubscriptionResponse:
    """Получить текущий план подписки пользователя.

    Args:
        current_user: Текущий авторизованный пользователь.
        unit_of_work: UnitOfWork для работы с БД.

    Returns:
        Информация о текущем плане подписки.

    Raises:
        HTTPException: 404 если подписка не найдена.
    """
    try:
        # Проверяем и обновляем подписку
        check_subscription_uc = CheckAndUpdateSubscriptionUseCase(
            user_subscription_repository=unit_of_work.user_subscription_repository,
            subscription_plan_repository=unit_of_work.subscription_plan_repository,
        )
        user_subscription, plan = await check_subscription_uc.execute(current_user.id)

        # Вычисляем дополнительные поля
        now = datetime.now(timezone.utc)
        next_reset_at = None
        seconds_until_reset = None
        if user_subscription.period_started_at is not None:
            next_reset_at = user_subscription.period_started_at.replace(
                tzinfo=timezone.utc
            ) + timedelta(seconds=plan.reset_period_seconds)
            elapsed = (now - user_subscription.period_started_at).total_seconds()
            seconds_until_reset = max(0, int(plan.reset_period_seconds - elapsed))

        days_remaining = None
        if user_subscription.expires_at is not None:
            delta = user_subscription.expires_at.replace(tzinfo=timezone.utc) - now
            days_remaining = max(0, delta.days)

        return UserSubscriptionResponse(
            plan_id=plan.id,
            plan_name=plan.name,
            response_limit=plan.response_limit,
            reset_period_seconds=plan.reset_period_seconds,
            responses_count=user_subscription.responses_count,
            period_started_at=user_subscription.period_started_at,
            next_reset_at=next_reset_at,
            seconds_until_reset=seconds_until_reset,
            started_at=user_subscription.started_at,
            expires_at=user_subscription.expires_at,
            days_remaining=days_remaining,
        )
    except ValueError as exc:
        logger.error(f"Ошибка при получении плана подписки: {exc}", exc_info=True)
        raise HTTPException(
            status_code=404, detail=f"Подписка не найдена: {exc}"
        ) from exc
    except Exception as exc:
        logger.error(f"Внутренняя ошибка при получении плана подписки: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при получении плана подписки"
        ) from exc


@router.get("/daily-responses", response_model=DailyResponsesResponse)
async def get_daily_responses(
    current_user: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
) -> DailyResponsesResponse:
    """Получить информацию о количестве откликов за текущий период.

    Args:
        current_user: Текущий авторизованный пользователь.
        unit_of_work: UnitOfWork для работы с БД.

    Returns:
        Информация о лимитах откликов.

    Raises:
        HTTPException: 404 если подписка не найдена.
    """
    try:
        # Проверяем и обновляем подписку
        check_subscription_uc = CheckAndUpdateSubscriptionUseCase(
            user_subscription_repository=unit_of_work.user_subscription_repository,
            subscription_plan_repository=unit_of_work.subscription_plan_repository,
        )
        user_subscription, plan = await check_subscription_uc.execute(current_user.id)

        # Вычисляем дополнительные поля
        now = datetime.now(timezone.utc)
        seconds_until_reset = None
        if user_subscription.period_started_at is not None:
            elapsed = (now - user_subscription.period_started_at).total_seconds()
            seconds_until_reset = max(0, int(plan.reset_period_seconds - elapsed))

        return DailyResponsesResponse(
            count=user_subscription.responses_count,
            limit=plan.response_limit,
            remaining=max(0, plan.response_limit - user_subscription.responses_count),
            period_started_at=user_subscription.period_started_at,
            seconds_until_reset=seconds_until_reset,
        )
    except ValueError as exc:
        logger.error(f"Ошибка при получении информации об откликах: {exc}", exc_info=True)
        raise HTTPException(
            status_code=404, detail=f"Подписка не найдена: {exc}"
        ) from exc
    except Exception as exc:
        logger.error(f"Внутренняя ошибка при получении информации об откликах: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при получении информации об откликах"
        ) from exc


@router.get("/plans", response_model=PlansListResponse)
async def get_all_plans(
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
) -> PlansListResponse:
    """Получить список всех доступных планов подписки.

    Args:
        unit_of_work: UnitOfWork для работы с БД.

    Returns:
        Список всех активных планов подписки.
    """
    try:
        plans = await unit_of_work.subscription_plan_repository.get_all()
        plans_list = [
            SubscriptionPlanResponse(
                id=plan.id,
                name=plan.name,
                response_limit=plan.response_limit,
                reset_period_seconds=plan.reset_period_seconds,
                duration_days=plan.duration_days,
                price=float(plan.price),
            )
            for plan in plans
        ]
        return PlansListResponse(
            plans=plans_list,
            total=len(plans_list),
            page=1,
            page_size=len(plans_list),
        )
    except Exception as exc:
        logger.error(
            "Внутренняя ошибка при получении списка планов", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при получении списка планов"
        ) from exc


@router.post("/change-plan", response_model=UserSubscriptionResponse)
async def change_plan(
    request: ChangePlanRequest,
    current_user: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
) -> UserSubscriptionResponse:
    """Изменить план подписки пользователя (тестовый эндпоинт без оплаты).

    Args:
        request: Запрос с названием нового плана.
        current_user: Текущий авторизованный пользователь.
        unit_of_work: UnitOfWork для работы с БД.

    Returns:
        Обновленная информация о подписке пользователя.

    Raises:
        HTTPException: 403 если пользователь не является администратором, 404 если план не найден, 400 при ошибках валидации.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Только администраторы могут менять план подписки"
        )
    
    try:
        change_subscription_uc = ChangeUserSubscriptionUseCase(
            user_subscription_repository=unit_of_work.user_subscription_repository,
            subscription_plan_repository=unit_of_work.subscription_plan_repository,
        )
        user_subscription, plan = await change_subscription_uc.execute(
            current_user.id, request.plan_name
        )

        # Вычисляем дополнительные поля для ответа
        now = datetime.now(timezone.utc)
        next_reset_at = None
        seconds_until_reset = None
        if user_subscription.period_started_at is not None:
            next_reset_at = user_subscription.period_started_at.replace(
                tzinfo=timezone.utc
            ) + timedelta(seconds=plan.reset_period_seconds)
            elapsed = (now - user_subscription.period_started_at).total_seconds()
            seconds_until_reset = max(0, int(plan.reset_period_seconds - elapsed))

        days_remaining = None
        if user_subscription.expires_at is not None:
            delta = user_subscription.expires_at.replace(tzinfo=timezone.utc) - now
            days_remaining = max(0, delta.days)

        return UserSubscriptionResponse(
            plan_id=plan.id,
            plan_name=plan.name,
            response_limit=plan.response_limit,
            reset_period_seconds=plan.reset_period_seconds,
            responses_count=user_subscription.responses_count,
            period_started_at=user_subscription.period_started_at,
            next_reset_at=next_reset_at,
            seconds_until_reset=seconds_until_reset,
            started_at=user_subscription.started_at or now,
            expires_at=user_subscription.expires_at,
            days_remaining=days_remaining,
        )
    except ValueError as exc:
        logger.error(
            f"Ошибка при смене плана подписки для user_id={current_user.id}: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=404, detail=f"План не найден или ошибка: {exc}"
        ) from exc
    except Exception as exc:
        logger.error(
            f"Внутренняя ошибка при смене плана подписки для user_id={current_user.id}: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при смене плана подписки"
        ) from exc
