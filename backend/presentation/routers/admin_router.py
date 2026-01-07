from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query

from application.services.admin_llm_service import AdminLlmService
from application.services.admin_plan_service import AdminPlanService
from application.services.admin_user_service import AdminUserService
from presentation.dependencies import (
    admin_only,
    get_admin_llm_service,
    get_admin_plan_service,
    get_admin_user_service,
)
from presentation.dto.admin_llm_call_response import (
    LlmCallListResponse,
    LlmCallResponse,
)
from presentation.dto.admin_metrics_response import (
    CombinedMetricsResponse,
    LlmUsageMetricsResponse,
    VacancyResponsesMetricsResponse,
)
from presentation.dto.admin_user_detail_response import (
    AdminChangeUserPlanRequest,
    AdminUserDetailResponse,
    AdminUserFlagsUpdateRequest,
)
from presentation.dto.subscription_response import (
    PlansListResponse,
    SubscriptionPlanResponse,
)
from presentation.dto.admin_plan_request import AdminPlanUpsertRequest
from presentation.dto.user_admin_response import AdminUserListResponse, AdminUserResponse


router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[Depends(admin_only)],
)


@router.get("/health")
async def admin_health():
    return {"status": "ok"}


@router.get(
    "/users",
    response_model=AdminUserListResponse,
    summary="Список пользователей для админки",
)
async def list_users_for_admin(
    phone: str | None = Query(
        default=None,
        description="Подстрока телефона для поиска (ILIKE)",
    ),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=200, description="Размер страницы"),
    admin_user_service: AdminUserService = Depends(get_admin_user_service),
) -> AdminUserListResponse:
    """Получить список пользователей для админской панели."""
    users, total = await admin_user_service.list_users(
        phone_substring=phone,
        page=page,
        page_size=page_size,
    )

    items = [AdminUserResponse.from_entity(user) for user in users]
    return AdminUserListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/users/{user_id}",
    response_model=AdminUserDetailResponse,
    summary="Детальная информация по пользователю",
)
async def get_user_detail_for_admin(
    user_id: UUID = Path(..., description="UUID пользователя"),
    admin_user_service: AdminUserService = Depends(get_admin_user_service),
) -> AdminUserDetailResponse:
    user, user_subscription, plan = await admin_user_service.get_user_detail(
        user_id=user_id
    )
    return AdminUserDetailResponse.from_entities(
        user=user,
        user_subscription=user_subscription,
        plan=plan,
    )


@router.patch(
    "/users/{user_id}/flags",
    response_model=AdminUserResponse,
    summary="Обновить флаги пользователя (is_active, is_verified)",
)
async def update_user_flags_for_admin(
    user_id: UUID = Path(..., description="UUID пользователя"),
    payload: AdminUserFlagsUpdateRequest | None = None,
    admin_user_service: AdminUserService = Depends(get_admin_user_service),
) -> AdminUserResponse:
    payload = payload or AdminUserFlagsUpdateRequest()
    user = await admin_user_service.update_user_flags(
        user_id=user_id,
        is_active=payload.is_active,
        is_verified=payload.is_verified,
    )
    return AdminUserResponse.from_entity(user)


@router.post(
    "/users/{user_id}/change-plan",
    response_model=AdminUserDetailResponse,
    summary="Сменить тарифный план пользователя",
)
async def change_user_plan_for_admin(
    user_id: UUID = Path(..., description="UUID пользователя"),
    payload: AdminChangeUserPlanRequest = ...,
    admin_user_service: AdminUserService = Depends(get_admin_user_service),
) -> AdminUserDetailResponse:
    await admin_user_service.change_user_subscription(
        user_id=user_id,
        plan_name=payload.plan_name,
    )
    # Возвращаем обновленные данные
    user, user_subscription, plan = await admin_user_service.get_user_detail(
        user_id=user_id
    )
    return AdminUserDetailResponse.from_entities(
        user=user,
        user_subscription=user_subscription,
        plan=plan,
    )


@router.delete(
    "/users/{user_id}",
    status_code=204,
    summary="Удалить пользователя и все связанные данные",
)
async def delete_user_for_admin(
    user_id: UUID = Path(..., description="UUID пользователя"),
    admin_user_service: AdminUserService = Depends(get_admin_user_service),
) -> None:
    await admin_user_service.delete_user(user_id=user_id)
    return None


@router.get(
    "/plans",
    response_model=PlansListResponse,
    summary="Список тарифных планов для админки",
)
async def list_plans_for_admin(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=200, description="Размер страницы"),
    admin_plan_service: AdminPlanService = Depends(get_admin_plan_service),
) -> PlansListResponse:
    plans, total = await admin_plan_service.list_plans(page=page, page_size=page_size)
    return PlansListResponse(
        plans=[
            SubscriptionPlanResponse(
                id=plan.id,
                name=plan.name,
                response_limit=plan.response_limit,
                reset_period_seconds=plan.reset_period_seconds,
                duration_days=plan.duration_days,
                price=float(plan.price),
            )
            for plan in plans
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/plans",
    response_model=SubscriptionPlanResponse,
    summary="Создать новый тарифный план",
)
async def create_plan_for_admin(
    payload: AdminPlanUpsertRequest,
    admin_plan_service: AdminPlanService = Depends(get_admin_plan_service),
) -> SubscriptionPlanResponse:
    plan = await admin_plan_service.upsert_plan(
        plan_id=None,
        name=payload.name,
        response_limit=payload.response_limit,
        reset_period_seconds=payload.reset_period_seconds,
        duration_days=payload.duration_days,
        price=float(payload.price),
        is_active=payload.is_active,
    )
    return SubscriptionPlanResponse(
        id=plan.id,
        name=plan.name,
        response_limit=plan.response_limit,
        reset_period_seconds=plan.reset_period_seconds,
        duration_days=plan.duration_days,
        price=float(plan.price),
    )


@router.put(
    "/plans/{plan_id}",
    response_model=SubscriptionPlanResponse,
    summary="Обновить тарифный план",
)
async def update_plan_for_admin(
    plan_id: UUID = Path(..., description="UUID плана"),
    payload: AdminPlanUpsertRequest = ...,
    admin_plan_service: AdminPlanService = Depends(get_admin_plan_service),
) -> SubscriptionPlanResponse:
    plan = await admin_plan_service.upsert_plan(
        plan_id=plan_id,
        name=payload.name,
        response_limit=payload.response_limit,
        reset_period_seconds=payload.reset_period_seconds,
        duration_days=payload.duration_days,
        price=float(payload.price),
        is_active=payload.is_active,
    )
    return SubscriptionPlanResponse(
        id=plan.id,
        name=plan.name,
        response_limit=plan.response_limit,
        reset_period_seconds=plan.reset_period_seconds,
        duration_days=plan.duration_days,
        price=float(plan.price),
    )


@router.patch(
    "/plans/{plan_id}/deactivate",
    response_model=SubscriptionPlanResponse,
    summary="Деактивировать тарифный план",
)
async def deactivate_plan_for_admin(
    plan_id: UUID = Path(..., description="UUID плана"),
    admin_plan_service: AdminPlanService = Depends(get_admin_plan_service),
) -> SubscriptionPlanResponse:
    plan = await admin_plan_service.deactivate_plan(plan_id=plan_id)
    return SubscriptionPlanResponse(
        id=plan.id,
        name=plan.name,
        response_limit=plan.response_limit,
        reset_period_seconds=plan.reset_period_seconds,
        duration_days=plan.duration_days,
        price=float(plan.price),
    )


@router.get(
    "/metrics/llm",
    response_model=LlmUsageMetricsResponse,
    summary="Метрики использования LLM",
)
async def get_llm_usage_metrics(
    start_date: datetime = Query(..., description="Начальная дата (включительно)"),
    end_date: datetime = Query(..., description="Конечная дата (включительно)"),
    plan_id: UUID | None = Query(None, description="Фильтр по ID плана подписки"),
    time_step: str = Query("day", description="Шаг группировки: day, week, month"),
    admin_llm_service: AdminLlmService = Depends(get_admin_llm_service),
) -> LlmUsageMetricsResponse:
    """Получить метрики использования LLM за период."""
    metrics_by_period, total_metrics = await admin_llm_service.get_llm_usage_metrics(
        start_date=start_date,
        end_date=end_date,
        plan_id=plan_id,
        time_step=time_step,
    )

    from presentation.dto.admin_metrics_response import (
        LlmPeriodMetric,
        LlmTotalMetrics,
    )

    return LlmUsageMetricsResponse(
        metrics_by_period=[
            LlmPeriodMetric(
                period_start=period_start,
                calls_count=calls_count,
                total_tokens=total_tokens,
                unique_users=unique_users,
            )
            for period_start, calls_count, total_tokens, unique_users in metrics_by_period
        ],
        total_metrics=LlmTotalMetrics(
            calls_count=total_metrics[0],
            total_tokens=total_metrics[1],
            unique_users=total_metrics[2],
            avg_tokens_per_user=total_metrics[3],
        ),
    )


@router.get(
    "/metrics/responses",
    response_model=VacancyResponsesMetricsResponse,
    summary="Метрики откликов на вакансии",
)
async def get_vacancy_responses_metrics(
    start_date: datetime = Query(..., description="Начальная дата (включительно)"),
    end_date: datetime = Query(..., description="Конечная дата (включительно)"),
    plan_id: UUID | None = Query(None, description="Фильтр по ID плана подписки"),
    time_step: str = Query("day", description="Шаг группировки: day, week, month"),
    admin_llm_service: AdminLlmService = Depends(get_admin_llm_service),
) -> VacancyResponsesMetricsResponse:
    """Получить метрики откликов на вакансии за период."""
    (
        metrics_by_period,
        total_metrics,
    ) = await admin_llm_service.get_vacancy_responses_metrics(
        start_date=start_date,
        end_date=end_date,
        plan_id=plan_id,
        time_step=time_step,
    )

    from presentation.dto.admin_metrics_response import (
        VacancyResponsePeriodMetric,
        VacancyResponseTotalMetrics,
    )

    return VacancyResponsesMetricsResponse(
        metrics_by_period=[
            VacancyResponsePeriodMetric(
                period_start=period_start,
                responses_count=responses_count,
                unique_users=unique_users,
            )
            for period_start, responses_count, unique_users in metrics_by_period
        ],
        total_metrics=VacancyResponseTotalMetrics(
            responses_count=total_metrics[0],
            unique_users=total_metrics[1],
            avg_responses_per_user=total_metrics[2],
        ),
    )


@router.get(
    "/metrics",
    response_model=CombinedMetricsResponse,
    summary="Комбинированные метрики LLM и откликов",
)
async def get_combined_metrics(
    start_date: datetime = Query(..., description="Начальная дата (включительно)"),
    end_date: datetime = Query(..., description="Конечная дата (включительно)"),
    plan_id: UUID | None = Query(None, description="Фильтр по ID плана подписки"),
    time_step: str = Query("day", description="Шаг группировки: day, week, month"),
    admin_llm_service: AdminLlmService = Depends(get_admin_llm_service),
) -> CombinedMetricsResponse:
    """Получить комбинированные метрики LLM и откликов за период."""
    llm_metrics_by_period, llm_total = await admin_llm_service.get_llm_usage_metrics(
        start_date=start_date,
        end_date=end_date,
        plan_id=plan_id,
        time_step=time_step,
    )

    (
        responses_metrics_by_period,
        responses_total,
    ) = await admin_llm_service.get_vacancy_responses_metrics(
        start_date=start_date,
        end_date=end_date,
        plan_id=plan_id,
        time_step=time_step,
    )

    from presentation.dto.admin_metrics_response import (
        LlmPeriodMetric,
        LlmTotalMetrics,
        LlmUsageMetricsResponse,
        VacancyResponsePeriodMetric,
        VacancyResponseTotalMetrics,
        VacancyResponsesMetricsResponse,
    )

    return CombinedMetricsResponse(
        llm_metrics=LlmUsageMetricsResponse(
            metrics_by_period=[
                LlmPeriodMetric(
                    period_start=period_start,
                    calls_count=calls_count,
                    total_tokens=total_tokens,
                    unique_users=unique_users,
                )
                for period_start, calls_count, total_tokens, unique_users in llm_metrics_by_period
            ],
            total_metrics=LlmTotalMetrics(
                calls_count=llm_total[0],
                total_tokens=llm_total[1],
                unique_users=llm_total[2],
                avg_tokens_per_user=llm_total[3],
            ),
        ),
        responses_metrics=VacancyResponsesMetricsResponse(
            metrics_by_period=[
                VacancyResponsePeriodMetric(
                    period_start=period_start,
                    responses_count=responses_count,
                    unique_users=unique_users,
                )
                for period_start, responses_count, unique_users in responses_metrics_by_period
            ],
            total_metrics=VacancyResponseTotalMetrics(
                responses_count=responses_total[0],
                unique_users=responses_total[1],
                avg_responses_per_user=responses_total[2],
            ),
        ),
    )


@router.get(
    "/llm-calls",
    response_model=LlmCallListResponse,
    summary="Список вызовов LLM для админки",
)
async def list_llm_calls_for_admin(
    start_date: datetime | None = Query(
        None, description="Начальная дата фильтра (включительно)"
    ),
    end_date: datetime | None = Query(
        None, description="Конечная дата фильтра (включительно)"
    ),
    user_id: UUID | None = Query(None, description="Фильтр по ID пользователя"),
    agent_name: str | None = Query(None, description="Фильтр по имени агента"),
    status: str | None = Query(None, description="Фильтр по статусу (success/error)"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=200, description="Размер страницы"),
    admin_llm_service: AdminLlmService = Depends(get_admin_llm_service),
) -> LlmCallListResponse:
    """Получить список вызовов LLM для админки с фильтрами и пагинацией."""
    calls, total = await admin_llm_service.list_llm_calls(
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        agent_name=agent_name,
        status=status,
        page=page,
        page_size=page_size,
    )

    return LlmCallListResponse(
        items=[LlmCallResponse.from_entity(call) for call in calls],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/llm-calls/{call_id}",
    response_model=LlmCallResponse,
    summary="Детальная информация о вызове LLM",
)
async def get_llm_call_detail_for_admin(
    call_id: UUID = Path(..., description="UUID записи о вызове LLM"),
    admin_llm_service: AdminLlmService = Depends(get_admin_llm_service),
) -> LlmCallResponse:
    """Получить детальную информацию о вызове LLM."""
    call = await admin_llm_service.get_llm_call_detail(call_id=call_id)
    if call is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Вызов LLM не найден")
    return LlmCallResponse.from_entity(call)


