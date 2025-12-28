"""Роутер для работы с резюме."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from loguru import logger

from application.services.resumes_service import ResumesService
from domain.interfaces.resume_service_port import ResumeServicePort
from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from infrastructure.auth.fastapi_users_setup import get_current_active_user
from infrastructure.clients.hh_client import HHHttpClient
from infrastructure.database.models.user_model import UserModel
from presentation.dependencies import (
    get_evaluate_resume_use_case,
    get_filter_settings_generation_service,
    get_unit_of_work,
)
from presentation.dto.resume_evaluation_response import ResumeEvaluationResponse
from presentation.dto.resume_request import CreateResumeRequest, UpdateResumeRequest
from presentation.dto.resume_response import ResumeResponse, ResumesListResponse
from presentation.dto.resume_filter_settings_dto import (
    ResumeFilterSettingsResponse,
    ResumeFilterSettingsUpdate,
)
from presentation.dto.user_filter_settings_dto import SuggestedUserFilterSettingsResponse

router = APIRouter(prefix="/api/resumes", tags=["resumes"])


def get_resumes_service(
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
) -> ResumeServicePort:
    """Dependency для получения ResumesService.

    Args:
        unit_of_work: UnitOfWork для управления транзакциями.

    Returns:
        ResumesService для работы с резюме.
    """
    from application.services.resumes_service import ResumesService

    return ResumesService(unit_of_work)


@router.post("", response_model=ResumeResponse, status_code=201)
async def create_resume(
    request: CreateResumeRequest,
    current_user: UserModel = Depends(get_current_active_user),
    service: ResumeServicePort = Depends(get_resumes_service),
) -> ResumeResponse:
    """Создать резюме для текущего пользователя."""
    try:
        resume = await service.create_resume(
            user_id=current_user.id,
            content=request.content,
            user_parameters=request.user_parameters,
        )
        return ResumeResponse.from_entity(resume)
    except Exception as exc:  # pragma: no cover - обёртка ошибок HTTP
        logger.error(f"Ошибка при создании резюме: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при создании резюме"
        ) from exc


@router.get("", response_model=ResumesListResponse)
async def list_resumes(
    current_user: UserModel = Depends(get_current_active_user),
    service: ResumeServicePort = Depends(get_resumes_service),
) -> ResumesListResponse:
    """Получить список резюме текущего пользователя."""
    try:
        resumes = await service.list_user_resumes(user_id=current_user.id)
        resume_responses = [ResumeResponse.from_entity(resume) for resume in resumes]
        return ResumesListResponse(count=len(resume_responses), items=resume_responses)
    except Exception as exc:  # pragma: no cover - обёртка ошибок HTTP
        logger.error(f"Ошибка при получении списка резюме: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при получении списка резюме"
        ) from exc


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: UUID,
    current_user: UserModel = Depends(get_current_active_user),
    service: ResumeServicePort = Depends(get_resumes_service),
) -> ResumeResponse:
    """Получить резюме по ID (с проверкой принадлежности)."""
    try:
        resume = await service.get_resume(resume_id=resume_id, user_id=current_user.id)
        if resume is None:
            raise HTTPException(
                status_code=404, detail=f"Резюме с ID {resume_id} не найдено"
            )

        return ResumeResponse.from_entity(resume)
    except PermissionError as exc:
        logger.warning(f"Попытка получить чужое резюме: {exc}")
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - обёртка ошибок HTTP
        logger.error(f"Ошибка при получении резюме: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при получении резюме"
        ) from exc


@router.put("/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: UUID,
    request: UpdateResumeRequest,
    current_user: UserModel = Depends(get_current_active_user),
    service: ResumeServicePort = Depends(get_resumes_service),
) -> ResumeResponse:
    """Обновить резюме (с проверкой принадлежности)."""
    try:
        resume = await service.update_resume(
            resume_id=resume_id,
            user_id=current_user.id,
            content=request.content,
            user_parameters=request.user_parameters,
            is_auto_reply=request.is_auto_reply,
            autolike_threshold=request.autolike_threshold,
        )
        return ResumeResponse.from_entity(resume)
    except PermissionError as exc:
        logger.warning(f"Попытка обновить чужое резюме: {exc}")
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        logger.error(f"Ошибка валидации: {exc}", exc_info=True)
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - обёртка ошибок HTTP
        logger.error(f"Ошибка при обновлении резюме: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при обновлении резюме"
        ) from exc


@router.delete("/{resume_id}", status_code=204)
async def delete_resume(
    resume_id: UUID,
    current_user: UserModel = Depends(get_current_active_user),
    service: ResumeServicePort = Depends(get_resumes_service),
) -> Response:
    """Удалить резюме (с проверкой принадлежности)."""
    try:
        await service.delete_resume(resume_id=resume_id, user_id=current_user.id)
        return Response(status_code=204)
    except PermissionError as exc:
        logger.warning(f"Попытка удалить чужое резюме: {exc}")
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        logger.error(f"Ошибка валидации: {exc}", exc_info=True)
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - обёртка ошибок HTTP
        logger.error(f"Ошибка при удалении резюме: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при удалении резюме"
        ) from exc


@router.get("/{resume_id}/filter-settings", response_model=ResumeFilterSettingsResponse)
async def get_resume_filter_settings(
    resume_id: UUID,
    current_user: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
    service: ResumeServicePort = Depends(get_resumes_service),
) -> ResumeFilterSettingsResponse:
    """Получить настройки фильтров вакансий для резюме."""
    try:
        # Проверяем принадлежность резюме
        resume = await service.get_resume(resume_id=resume_id, user_id=current_user.id)
        if resume is None:
            raise HTTPException(
                status_code=404, detail=f"Резюме с ID {resume_id} не найдено"
            )

        # Получаем настройки фильтров
        settings = await unit_of_work.resume_filter_settings_repository.get_by_resume_id(
            resume_id
        )

        if settings is None:
            # Инициализируем пустыми настройками
            from domain.entities.resume_filter_settings import ResumeFilterSettings

            settings = ResumeFilterSettings(resume_id=resume_id)

        return ResumeFilterSettingsResponse.from_entity(settings)
    except PermissionError as exc:
        logger.warning(f"Попытка получить настройки чужого резюме: {exc}")
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - обёртка ошибок HTTP
        logger.error(
            f"Ошибка при получении настроек фильтров резюме: {exc}", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при получении настроек фильтров"
        ) from exc


@router.put("/{resume_id}/filter-settings", response_model=ResumeFilterSettingsResponse)
async def update_resume_filter_settings(
    resume_id: UUID,
    request: ResumeFilterSettingsUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
    service: ResumeServicePort = Depends(get_resumes_service),
) -> ResumeFilterSettingsResponse:
    """Обновить настройки фильтров вакансий для резюме."""
    try:
        # Проверяем принадлежность резюме
        resume = await service.get_resume(resume_id=resume_id, user_id=current_user.id)
        if resume is None:
            raise HTTPException(
                status_code=404, detail=f"Резюме с ID {resume_id} не найдено"
            )

        # Получаем существующие настройки
        existing = await unit_of_work.resume_filter_settings_repository.get_by_resume_id(
            resume_id
        )

        from domain.entities.resume_filter_settings import ResumeFilterSettings

        settings = ResumeFilterSettings(
            resume_id=resume_id,
            text=(
                request.text if request.text is not None else (existing.text if existing else None)
            ),
            hh_resume_id=(
                request.hh_resume_id
                if request.hh_resume_id is not None
                else (existing.hh_resume_id if existing else None)
            ),
            experience=(
                request.experience
                if request.experience is not None
                else (existing.experience if existing else None)
            ),
            employment=(
                request.employment
                if request.employment is not None
                else (existing.employment if existing else None)
            ),
            schedule=(
                request.schedule
                if request.schedule is not None
                else (existing.schedule if existing else None)
            ),
            professional_role=(
                request.professional_role
                if request.professional_role is not None
                else (existing.professional_role if existing else None)
            ),
            area=(
                request.area if request.area is not None else (existing.area if existing else None)
            ),
            salary=(
                request.salary
                if request.salary is not None
                else (existing.salary if existing else None)
            ),
            currency=(
                request.currency
                if request.currency is not None
                else (existing.currency if existing else None)
            ),
            only_with_salary=(
                request.only_with_salary
                if request.only_with_salary is not None
                else (existing.only_with_salary if existing else False)
            ),
            order_by=(
                request.order_by
                if request.order_by is not None
                else (existing.order_by if existing else None)
            ),
            period=(
                request.period
                if request.period is not None
                else (existing.period if existing else None)
            ),
            date_from=(
                request.date_from
                if request.date_from is not None
                else (existing.date_from if existing else None)
            ),
            date_to=(
                request.date_to
                if request.date_to is not None
                else (existing.date_to if existing else None)
            ),
        )

        saved = await unit_of_work.resume_filter_settings_repository.upsert_for_resume(
            resume_id=resume_id,
            settings=settings,
        )
        await unit_of_work.commit()

        return ResumeFilterSettingsResponse.from_entity(saved)
    except PermissionError as exc:
        logger.warning(f"Попытка обновить настройки чужого резюме: {exc}")
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - обёртка ошибок HTTP
        logger.error(
            f"Ошибка при обновлении настроек фильтров резюме: {exc}", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при обновлении настроек фильтров"
        ) from exc


@router.post(
    "/{resume_id}/filter-settings/suggest",
    response_model=SuggestedUserFilterSettingsResponse,
)
async def suggest_resume_filter_settings(
    resume_id: UUID,
    current_user: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
    service: ResumeServicePort = Depends(get_resumes_service),
    filter_service=Depends(get_filter_settings_generation_service),
) -> SuggestedUserFilterSettingsResponse:
    """Сгенерировать предложенные настройки фильтров для резюме.

    Использует LLM-агент и не сохраняет результат в БД.

    Args:
        resume_id: UUID резюме для генерации настроек.
        current_user: Текущий авторизованный пользователь.
        unit_of_work: UnitOfWork для работы с БД.
        service: Сервис работы с резюме.
        filter_service: Сервис генерации настроек фильтров.

    Returns:
        Предложенные настройки фильтров.

    Raises:
        HTTPException: 400 при ошибках валидации,
            403 если резюме не принадлежит пользователю,
            404 если резюме не найдено,
            500 при внутренних ошибках.
    """
    try:
        # Проверяем принадлежность резюме
        resume = await service.get_resume(resume_id=resume_id, user_id=current_user.id)
        if resume is None:
            raise HTTPException(
                status_code=404, detail=f"Резюме с ID {resume_id} не найдено"
            )

        suggested = await filter_service.generate_for_resume(resume)
        return SuggestedUserFilterSettingsResponse(
            text=suggested.text,
            salary=suggested.salary,
            currency=suggested.currency,
        )
    except PermissionError as exc:
        logger.warning(f"Попытка получить предложения для чужого резюме: {exc}")
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - обёртка ошибок HTTP
        logger.error(
            f"Внутренняя ошибка при генерации настроек фильтров: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка при генерации настроек фильтров",
        ) from exc


@router.post("/{resume_id}/evaluate", response_model=ResumeEvaluationResponse)
async def evaluate_resume(
    resume_id: UUID,
    current_user: UserModel = Depends(get_current_active_user),
    service: ResumeServicePort = Depends(get_resumes_service),
    evaluate_uc=Depends(get_evaluate_resume_use_case),
) -> ResumeEvaluationResponse:
    """Оценить резюме на основе правил."""
    try:
        # Проверяем принадлежность резюме
        resume = await service.get_resume(resume_id=resume_id, user_id=current_user.id)
        if resume is None:
            raise HTTPException(
                status_code=404, detail=f"Резюме с ID {resume_id} не найдено"
            )

        if not resume.content:
            raise HTTPException(
                status_code=400, detail="Текст резюме пуст"
            )

        result = await evaluate_uc.execute(resume.content)
        return ResumeEvaluationResponse(**result)
    except PermissionError as exc:
        logger.warning(f"Попытка оценить чужое резюме: {exc}")
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Ошибка при оценке резюме: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при оценке резюме"
        ) from exc


@router.post("/import-from-hh", response_model=ResumesListResponse)
async def import_resumes_from_hh(
    current_user: UserModel = Depends(get_current_active_user),
    service: ResumeServicePort = Depends(get_resumes_service),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
) -> ResumesListResponse:
    """Импортировать резюме из HeadHunter для текущего пользователя."""
    try:
        # Получаем HH auth data
        auth_data = await unit_of_work.user_hh_auth_data_repository.get_by_user_id(
            current_user.id
        )
        if auth_data is None:
            raise HTTPException(
                status_code=400, detail="HH auth data not set. Please configure HeadHunter authentication."
            )

        # Создаем HH клиент
        hh_client = HHHttpClient()

        # Импортируем резюме
        resumes = await service.import_resume_from_hh(
            user_id=current_user.id,
            hh_client=hh_client,
            headers=auth_data.headers,
            cookies=auth_data.cookies,
        )

        resume_responses = [ResumeResponse.from_entity(resume) for resume in resumes]
        return ResumesListResponse(count=len(resume_responses), items=resume_responses)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - обёртка ошибок HTTP
        logger.error(f"Ошибка при импорте резюме из HeadHunter: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при импорте резюме из HeadHunter"
        ) from exc
