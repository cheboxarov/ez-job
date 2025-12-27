"""Реализация репозитория пользователя."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.user import User
from domain.interfaces.user_repository_port import UserRepositoryPort
from infrastructure.database.models.user_model import UserModel


class UserRepository(UserRepositoryPort):
    """Реализация репозитория пользователя для SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория.

        Args:
            session: Async сессия SQLAlchemy.
        """
        self._session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Получить пользователя по ID.

        Args:
            user_id: UUID пользователя.

        Returns:
            Доменная сущность User или None, если пользователь не найден.
        """
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def get_first(self) -> User | None:
        """Получить первого пользователя из БД.

        Returns:
            Доменная сущность User или None, если пользователи не найдены.
        """
        stmt = select(UserModel).order_by(UserModel.id).limit(1)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def list_all(self) -> list[User]:
        """Получить всех пользователей из БД.

        Returns:
            Список доменных сущностей User.
        """
        stmt = select(UserModel).order_by(UserModel.id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(model) for model in models]

    async def update(self, user: User) -> User:
        """Обновить пользователя.

        Args:
            user: Доменная сущность User с обновленными данными.

        Returns:
            Обновленная доменная сущность User.

        Raises:
            ValueError: Если пользователь с таким ID не найден.
        """
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            raise ValueError(f"Пользователь с ID {user.id} не найден")

        # User теперь содержит только id, обновлять нечего
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_domain(model)

    def _to_domain(self, model: UserModel) -> User:
        """Преобразовать SQLAlchemy модель в доменную сущность.

        Args:
            model: SQLAlchemy модель UserModel.

        Returns:
            Доменная сущность User.
        """
        return User(id=model.id)

