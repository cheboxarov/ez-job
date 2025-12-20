"""Роутер для справочников (regions/areas и др.)."""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from domain.use_cases.get_areas import GetAreasUseCase
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase
from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from presentation.dependencies import (
    get_areas_use_case,
    get_cookies,
    get_current_user,
    get_headers,
    get_unit_of_work,
)

router = APIRouter(prefix="/api/dictionaries", tags=["dictionaries"])


@router.get("/areas")
async def get_areas(
    headers: Dict[str, str] = Depends(get_headers),
    cookies: Dict[str, str] = Depends(get_cookies),
    use_case: GetAreasUseCase = Depends(get_areas_use_case),
    current_user=Depends(get_current_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
) -> List[Dict[str, Any]]:
    """Получить дерево регионов HH (/areas) с проксированием структуры как есть."""
    try:
        # Создаем use case для обновления cookies
        update_cookies_uc = UpdateUserHhAuthCookiesUseCase(
            unit_of_work.user_hh_auth_data_repository
        )
        return await use_case.execute(
            headers=headers,
            cookies=cookies,
            user_id=current_user.id,
            update_cookies_uc=update_cookies_uc,
        )
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - обёртка ошибок HTTP
        logger.error(f"Ошибка при получении справочника регионов: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка при получении справочника регионов",
        ) from exc

