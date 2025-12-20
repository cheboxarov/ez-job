"""Фабрика для создания компонентов работы с БД."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from config import DatabaseConfig
from infrastructure.database.session import create_session_factory
from infrastructure.database.unit_of_work import UnitOfWork


def create_unit_of_work(config: DatabaseConfig) -> UnitOfWork:
    """Создает UnitOfWork с сессией.

    Args:
        config: Конфигурация базы данных.

    Returns:
        UnitOfWork для управления транзакциями.
    """
    session_factory = create_session_factory(config)
    return UnitOfWork(session_factory)


async def get_db_session(config: DatabaseConfig) -> AsyncSession:
    """Dependency для получения async сессии БД (для FastAPI Users).

    Args:
        config: Конфигурация базы данных.

    Yields:
        Async сессия SQLAlchemy.
    """
    session_factory = create_session_factory(config)
    async with session_factory() as session:
        yield session

