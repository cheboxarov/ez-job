"""Настройка FastAPI Users для аутентификации и авторизации."""

from __future__ import annotations

from typing import AsyncGenerator
from uuid import UUID

from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from config import load_config
from infrastructure.database.models.user_model import UserModel
from infrastructure.database.session import create_session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency для получения async сессии БД."""
    config = load_config()
    session_factory = create_session_factory(config.database)
    async with session_factory() as session:
        yield session


class UserManager(UUIDIDMixin, BaseUserManager[UserModel, UUID]):
    """Менеджер пользователей для FastAPI Users."""

    reset_password_token_secret = "SECRET"  # TODO: Вынести в конфиг
    verification_token_secret = "SECRET"  # TODO: Вынести в конфиг

    async def on_after_register(self, user: UserModel, request=None):
        """Вызывается после регистрации пользователя."""
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: UserModel, token: str, request=None
    ):
        """Вызывается после запроса восстановления пароля."""
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: UserModel, token: str, request=None
    ):
        """Вызывается после запроса верификации."""
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_db(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    """Dependency для получения адаптера пользователей."""
    yield SQLAlchemyUserDatabase(session, UserModel)


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    """Dependency для получения менеджера пользователей."""
    yield UserManager(user_db)


def get_jwt_strategy() -> JWTStrategy:
    """Получить стратегию JWT для аутентификации."""
    config = load_config()
    # TODO: Вынести SECRET в конфиг
    return JWTStrategy(secret="SECRET", lifetime_seconds=3600)


bearer_transport = BearerTransport(tokenUrl="/auth/login")

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# Создаем FastAPI Users
fastapi_users = FastAPIUsers[UserModel, UUID](get_user_manager, [auth_backend])

# Экспортируем зависимости
get_current_active_user = fastapi_users.current_user(active=True)
get_current_superuser = fastapi_users.current_user(active=True, superuser=True)

