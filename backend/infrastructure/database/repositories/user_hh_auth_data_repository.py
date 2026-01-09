"""Реализация репозитория для HH auth data пользователя."""

from __future__ import annotations

import json
import os
import sys
from typing import Union
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.sql import func

from domain.entities.user_hh_auth_data import UserHhAuthData
from domain.exceptions.lock_not_acquired import LockNotAcquiredError
from domain.interfaces.user_hh_auth_data_repository_port import (
    UserHhAuthDataRepositoryPort,
)
from infrastructure.database.models.user_model import UserModel
from infrastructure.database.repositories.base_repository import BaseRepository


# region agent log
def _debug_log(hypothesis_id: str, location: str, message: str, data: dict) -> None:
    try:
        Path("/Users/apple/dev/hh/.cursor/debug.log").open("a", encoding="utf-8").write(
            json.dumps(
                {
                    "sessionId": "hh-deadlock",
                    "runId": "pre-fix",
                    "hypothesisId": hypothesis_id,
                    "location": location,
                    "message": message,
                    "data": data,
                    "pid": os.getpid(),
                    "process": sys.argv[0] if sys.argv else None,
                    "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
                },
                ensure_ascii=False,
            )
            + "\n"
        )
    except Exception:
        pass
# endregion


class UserHhAuthDataRepository(BaseRepository, UserHhAuthDataRepositoryPort):
    """Реализация репозитория для HH auth data пользователя."""

    def __init__(
        self, 
        session_or_factory: Union[AsyncSession, async_sessionmaker[AsyncSession]]
    ) -> None:
        """Инициализация репозитория.

        Args:
            session_or_factory: Либо AsyncSession (для транзакционного режима),
                               либо async_sessionmaker (для standalone режима).
        """
        super().__init__(session_or_factory)

    async def get_by_user_id(
        self, user_id: UUID, *, with_for_update: bool = False
    ) -> UserHhAuthData | None:
        """Получить HH auth data по user_id из таблицы users.

        Args:
            user_id: UUID пользователя.
            with_for_update: Использовать SELECT ... FOR UPDATE (блокировка строки).

        Returns:
            Доменная сущность UserHhAuthData или None, если не найдено.
        """
        async with self._get_session() as session:
            _debug_log(
                "H2",
                "user_hh_auth_data_repository.get_by_user_id:enter",
                "select user row",
                {"user_id": str(user_id), "with_for_update": with_for_update, "session_id": id(session)},
            )

            # Межпроцессная синхронизация обновления HH cookies:
            # когда мы хотим блокировать строку пользователя (FOR UPDATE), дополнительно берём
            # advisory lock на время транзакции. Это предотвращает дедлоки между API-сервером и воркерами,
            # которые одновременно обновляют hh_cookies/hh_headers для одного user_id.
            if with_for_update:
                u = user_id.int
                k1 = (u >> 96) & 0xFFFFFFFF
                k2 = u & 0xFFFFFFFF

                # Приводим к signed int32, чтобы гарантированно влазило в Postgres int4
                if k1 >= 2**31:
                    k1 -= 2**32
                if k2 >= 2**31:
                    k2 -= 2**32

                _debug_log(
                    "H5",
                    "user_hh_auth_data_repository.get_by_user_id:before_advisory_lock",
                    "acquiring pg_try_advisory_xact_lock",
                    {"user_id": str(user_id), "k1": k1, "k2": k2, "session_id": id(session)},
                )
                lock_result = await session.execute(
                    text("SELECT pg_try_advisory_xact_lock(:k1, :k2)"),
                    {"k1": k1, "k2": k2},
                )
                is_locked = lock_result.scalar()
                if not is_locked:
                    _debug_log(
                        "H5",
                        "user_hh_auth_data_repository.get_by_user_id:lock_failed",
                        "pg_try_advisory_xact_lock failed - lock busy",
                        {"user_id": str(user_id), "session_id": id(session)},
                    )
                    raise LockNotAcquiredError(f"Could not acquire lock for user_id={user_id}")
                _debug_log(
                    "H5",
                    "user_hh_auth_data_repository.get_by_user_id:after_advisory_lock",
                    "pg_try_advisory_xact_lock acquired",
                    {"user_id": str(user_id), "session_id": id(session)},
                )

            stmt = select(UserModel).where(UserModel.id == user_id)

            if with_for_update:
                stmt = stmt.with_for_update()

            result = await session.execute(stmt)
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
        """Создать или обновить HH auth data для пользователя в таблице users.

        Args:
            user_id: UUID пользователя.
            headers: Словарь headers для HH API.
            cookies: Словарь cookies для HH API.

        Returns:
            Сохраненная доменная сущность UserHhAuthData.
        """
        async with self._get_session() as session:
            _debug_log(
                "H3",
                "user_hh_auth_data_repository.upsert:enter",
                "update user hh cookies/headers",
                {"user_id": str(user_id), "session_id": id(session)},
            )
            stmt = (
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(
                    hh_headers=headers,
                    hh_cookies=cookies,
                    hh_cookies_updated_at=func.now(),
                )
                .returning(UserModel)
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                raise ValueError(f"User with id={user_id} not found for HH auth update")
            await session.flush()
            return self._to_domain(model)

    async def delete(self, user_id: UUID) -> None:
        """Удалить HH auth data для пользователя (очистить HH поля в users).

        Args:
            user_id: UUID пользователя.
        """
        async with self._get_session() as session:
            stmt = (
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(hh_headers=None, hh_cookies=None)
            )
            await session.execute(stmt)
            await session.flush()

    def _to_domain(self, model: UserModel) -> UserHhAuthData:
        """Преобразовать UserModel в доменную сущность HH auth data.

        Args:
            model: SQLAlchemy модель UserModel.

        Returns:
            Доменная сущность UserHhAuthData.
        """
        return UserHhAuthData(
            user_id=model.id,
            headers=model.hh_headers or {},
            cookies=model.hh_cookies or {},
            cookies_updated_at=model.hh_cookies_updated_at,
        )
