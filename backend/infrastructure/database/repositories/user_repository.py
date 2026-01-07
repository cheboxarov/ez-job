"""Реализация репозитория пользователя."""

from __future__ import annotations

from typing import Union
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from domain.entities.user import User
from domain.interfaces.user_repository_port import UserRepositoryPort
from infrastructure.database.models.user_model import UserModel
from infrastructure.database.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository, UserRepositoryPort):
    """Реализация репозитория пользователя для SQLAlchemy."""

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

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Получить пользователя по ID.

        Args:
            user_id: UUID пользователя.

        Returns:
            Доменная сущность User или None, если пользователь не найден.
        """
        async with self._get_session() as session:
            stmt = select(UserModel).where(UserModel.id == user_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._to_domain(model)

    async def get_first(self) -> User | None:
        """Получить первого пользователя из БД.

        Returns:
            Доменная сущность User или None, если пользователи не найдены.
        """
        async with self._get_session() as session:
            stmt = select(UserModel).order_by(UserModel.id).limit(1)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._to_domain(model)

    async def list_all(self) -> list[User]:
        """Получить всех пользователей из БД.

        Returns:
            Список доменных сущностей User.
        """
        async with self._get_session() as session:
            stmt = select(UserModel).order_by(UserModel.id)
            result = await session.execute(stmt)
            models = result.scalars().all()

            return [self._to_domain(model) for model in models]

    async def search_for_admin(
        self,
        phone_substring: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[User], int]:
        """Поиск пользователей для админки с фильтрацией по телефону и пагинацией."""
        async with self._get_session() as session:
            stmt = select(UserModel)

            if phone_substring:
                pattern = f"%{phone_substring}%"
                stmt = stmt.where(UserModel.phone.ilike(pattern))

            count_stmt = stmt.with_only_columns(func.count()).order_by(None)
            total_result = await session.execute(count_stmt)
            total = int(total_result.scalar_one() or 0)

            offset = max(page - 1, 0) * page_size
            stmt = stmt.order_by(UserModel.id).offset(offset).limit(page_size)

            result = await session.execute(stmt)
            models = result.scalars().all()

            return [self._to_domain(model) for model in models], total

    async def update(self, user: User) -> User:
        """Обновить пользователя.

        Args:
            user: Доменная сущность User с обновленными данными.

        Returns:
            Обновленная доменная сущность User.

        Raises:
            ValueError: Если пользователь с таким ID не найден.
        """
        async with self._get_session() as session:
            stmt = select(UserModel).where(UserModel.id == user.id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                raise ValueError(f"Пользователь с ID {user.id} не найден")

            model.email = user.email or model.email
            model.phone = user.phone or model.phone
            model.is_active = user.is_active
            model.is_superuser = user.is_superuser
            model.is_verified = user.is_verified

            await session.flush()
            await session.refresh(model)

            return self._to_domain(model)

    async def delete(self, user_id: UUID) -> None:
        """Удалить пользователя по ID."""
        async with self._get_session() as session:
            stmt = select(UserModel).where(UserModel.id == user_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                raise ValueError(f"Пользователь с ID {user_id} не найден")

            await session.delete(model)
            await session.flush()

    def _to_domain(self, model: UserModel) -> User:
        """Преобразовать SQLAlchemy модель в доменную сущность.

        Args:
            model: SQLAlchemy модель UserModel.

        Returns:
            Доменная сущность User.
        """
        return User(
            id=model.id,
            email=model.email,
            phone=model.phone,
            is_active=model.is_active,
            is_superuser=model.is_superuser,
            is_verified=model.is_verified,
            created_at=getattr(model, "created_at", None),
        )

