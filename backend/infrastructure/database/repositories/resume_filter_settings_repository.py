"""Репозиторий настроек фильтров резюме для SQLAlchemy."""

from __future__ import annotations

import json
from typing import Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from domain.entities.resume_filter_settings import ResumeFilterSettings
from domain.interfaces.resume_filter_settings_repository_port import (
    ResumeFilterSettingsRepositoryPort,
)
from infrastructure.database.models.resume_filter_settings_model import (
    ResumeFilterSettingsModel,
)
from infrastructure.database.repositories.base_repository import BaseRepository


def _loads_list(value: str | None) -> list[str] | None:
    if not value:
        return None
    try:
        data = json.loads(value)
        if isinstance(data, list):
            return [str(x) for x in data]
    except Exception:
        # Фоллбэк на старый формат, если когда‑нибудь появится
        return [v for v in value.split(",") if v]
    return None


def _dumps_list(value: list[str] | None) -> str | None:
    if not value:
        return None
    return json.dumps(list(value), ensure_ascii=False)


class ResumeFilterSettingsRepository(BaseRepository, ResumeFilterSettingsRepositoryPort):
    """Реализация репозитория настроек фильтров резюме."""

    def __init__(
        self, 
        session_or_factory: Union[AsyncSession, async_sessionmaker[AsyncSession]]
    ) -> None:
        super().__init__(session_or_factory)

    async def get_by_resume_id(self, resume_id: UUID) -> ResumeFilterSettings | None:
        async with self._get_session() as session:
            stmt = select(ResumeFilterSettingsModel).where(
                ResumeFilterSettingsModel.resume_id == resume_id
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                return None
            return self._to_domain(model)

    async def upsert_for_resume(
        self,
        resume_id: UUID,
        settings: ResumeFilterSettings,
    ) -> ResumeFilterSettings:
        async with self._get_session() as session:
            stmt = select(ResumeFilterSettingsModel).where(
                ResumeFilterSettingsModel.resume_id == resume_id
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                model = ResumeFilterSettingsModel(resume_id=resume_id)
                session.add(model)

            model.text = settings.text
            model.hh_resume_id = settings.hh_resume_id

            model.experience = _dumps_list(settings.experience)
            model.employment = _dumps_list(settings.employment)
            model.schedule = _dumps_list(settings.schedule)
            model.professional_role = _dumps_list(settings.professional_role)

            model.area = settings.area
            model.salary = settings.salary
            model.currency = settings.currency
            model.only_with_salary = settings.only_with_salary

            model.order_by = settings.order_by
            model.period = settings.period
            model.date_from = settings.date_from
            model.date_to = settings.date_to

            await session.flush()
            await session.refresh(model)
            return self._to_domain(model)

    @staticmethod
    def _to_domain(model: ResumeFilterSettingsModel) -> ResumeFilterSettings:
        return ResumeFilterSettings(
            resume_id=model.resume_id,
            text=model.text,
            hh_resume_id=model.hh_resume_id,
            experience=_loads_list(model.experience),
            employment=_loads_list(model.employment),
            schedule=_loads_list(model.schedule),
            professional_role=_loads_list(model.professional_role),
            area=model.area,
            salary=model.salary,
            currency=model.currency,
            only_with_salary=bool(model.only_with_salary),
            order_by=model.order_by,
            period=model.period,
            date_from=model.date_from,
            date_to=model.date_to,
        )
