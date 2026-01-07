"""Репозиторий настроек фильтров пользователя для SQLAlchemy."""

from __future__ import annotations

import json
from typing import Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from domain.entities.user_filter_settings import UserFilterSettings
from domain.interfaces.user_filter_settings_repository_port import (
    UserFilterSettingsRepositoryPort,
)
from infrastructure.database.models.user_filter_settings_model import (
    UserFilterSettingsModel,
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


class UserFilterSettingsRepository(BaseRepository, UserFilterSettingsRepositoryPort):
    """Реализация репозитория настроек фильтров пользователя."""

    def __init__(
        self, 
        session_or_factory: Union[AsyncSession, async_sessionmaker[AsyncSession]]
    ) -> None:
        super().__init__(session_or_factory)

    async def get_by_user_id(self, user_id: UUID) -> UserFilterSettings | None:
        async with self._get_session() as session:
            stmt = select(UserFilterSettingsModel).where(
                UserFilterSettingsModel.user_id == user_id
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                return None
            return self._to_domain(model)

    async def upsert_for_user(
        self,
        user_id: UUID,
        settings: UserFilterSettings,
    ) -> UserFilterSettings:
        async with self._get_session() as session:
            stmt = select(UserFilterSettingsModel).where(
                UserFilterSettingsModel.user_id == user_id
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                model = UserFilterSettingsModel(user_id=user_id)
                session.add(model)

            model.text = settings.text
            model.resume_id = settings.resume_id

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
    def _to_domain(model: UserFilterSettingsModel) -> UserFilterSettings:
        return UserFilterSettings(
            user_id=model.user_id,
            text=model.text,
            resume_id=model.resume_id,
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


