"""Реализация репозитория токенов привязки Telegram."""

from __future__ import annotations

from typing import Union
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from domain.entities.telegram_link_token import TelegramLinkToken
from domain.interfaces.telegram_link_token_repository_port import TelegramLinkTokenRepositoryPort
from infrastructure.database.models.telegram_link_token_model import TelegramLinkTokenModel
from infrastructure.database.repositories.base_repository import BaseRepository


class TelegramLinkTokenRepository(BaseRepository, TelegramLinkTokenRepositoryPort):
    """Реализация репозитория токенов привязки Telegram для SQLAlchemy."""

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

    async def create(self, token: TelegramLinkToken) -> TelegramLinkToken:
        """Создать токен.

        Args:
            token: Доменная сущность TelegramLinkToken для создания.

        Returns:
            Созданная доменная сущность TelegramLinkToken с заполненными id и created_at.
        """
        async with self._get_session() as session:
            token_id = token.id if token.id else uuid4()
            now = datetime.now(timezone.utc)

            model = TelegramLinkTokenModel(
                id=token_id,
                user_id=token.user_id,
                token=token.token,
                expires_at=token.expires_at,
                created_at=token.created_at if token.created_at else now,
            )
            session.add(model)
            await session.flush()
            await session.refresh(model)
            return self._to_domain(model)

    async def get_by_token(self, token_str: str) -> TelegramLinkToken | None:
        """Получить токен по строке токена.

        Args:
            token_str: Строка токена.

        Returns:
            Доменная сущность TelegramLinkToken или None, если не найдено.
        """
        async with self._get_session() as session:
            stmt = select(TelegramLinkTokenModel).where(TelegramLinkTokenModel.token == token_str)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._to_domain(model)

    async def delete_by_user_id(self, user_id: UUID) -> None:
        """Удалить все токены пользователя.

        Args:
            user_id: UUID пользователя.
        """
        async with self._get_session() as session:
            stmt = delete(TelegramLinkTokenModel).where(TelegramLinkTokenModel.user_id == user_id)
            await session.execute(stmt)
            await session.flush()

    async def delete_expired(self) -> None:
        """Удалить все истёкшие токены."""
        async with self._get_session() as session:
            now = datetime.now(timezone.utc)
            stmt = delete(TelegramLinkTokenModel).where(TelegramLinkTokenModel.expires_at < now)
            await session.execute(stmt)
            await session.flush()

    def _to_domain(self, model: TelegramLinkTokenModel) -> TelegramLinkToken:
        """Преобразовать SQLAlchemy модель в доменную сущность.

        Args:
            model: SQLAlchemy модель TelegramLinkTokenModel.

        Returns:
            Доменная сущность TelegramLinkToken.
        """
        return TelegramLinkToken(
            id=model.id,
            user_id=model.user_id,
            token=model.token,
            expires_at=model.expires_at,
            created_at=model.created_at,
        )
