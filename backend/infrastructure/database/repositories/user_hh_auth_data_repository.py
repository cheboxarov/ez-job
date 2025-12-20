"""Реализация репозитория для HH auth data пользователя."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from domain.entities.user_hh_auth_data import UserHhAuthData
from domain.interfaces.user_hh_auth_data_repository_port import (
    UserHhAuthDataRepositoryPort,
)
from infrastructure.database.models.user_hh_auth_data_model import UserHhAuthDataModel


class UserHhAuthDataRepository(UserHhAuthDataRepositoryPort):
    """Реализация репозитория для HH auth data пользователя."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория.

        Args:
            session: Async сессия SQLAlchemy.
        """
        self._session = session

    async def get_by_user_id(self, user_id: UUID) -> UserHhAuthData | None:
        """Получить HH auth data по user_id.

        Args:
            user_id: UUID пользователя.

        Returns:
            Доменная сущность UserHhAuthData или None, если не найдено.
        """
        stmt = select(UserHhAuthDataModel).where(
            UserHhAuthDataModel.user_id == user_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def upsert(
        self,
        user_id: UUID,
        headers: dict[str, str],
        cookies: dict[str, str],
    ) -> UserHhAuthData:
        """Создать или обновить HH auth data для пользователя.

        Args:
            user_id: UUID пользователя.
            headers: Словарь headers для HH API.
            cookies: Словарь cookies для HH API.

        Returns:
            Сохраненная доменная сущность UserHhAuthData.
        """
        # Используем PostgreSQL INSERT ... ON CONFLICT для upsert
        stmt = (
            insert(UserHhAuthDataModel)
            .values(
                user_id=user_id,
                headers=headers,
                cookies=cookies,
            )
            .on_conflict_do_update(
                constraint="uq_user_hh_auth_data_user_id",
                set_={
                    "headers": headers,
                    "cookies": cookies,
                },
            )
            .returning(UserHhAuthDataModel)
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one()
        await self._session.flush()

        return self._to_domain(model)

    async def delete(self, user_id: UUID) -> None:
        """Удалить HH auth data для пользователя.

        Args:
            user_id: UUID пользователя.
        """
        stmt = select(UserHhAuthDataModel).where(
            UserHhAuthDataModel.user_id == user_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is not None:
            await self._session.delete(model)
            await self._session.flush()

    def _to_domain(self, model: UserHhAuthDataModel) -> UserHhAuthData:
        """Преобразовать SQLAlchemy модель в доменную сущность.

        Args:
            model: SQLAlchemy модель UserHhAuthDataModel.

        Returns:
            Доменная сущность UserHhAuthData.
        """
        return UserHhAuthData(
            user_id=model.user_id,
            headers=model.headers,
            cookies=model.cookies,
        )
