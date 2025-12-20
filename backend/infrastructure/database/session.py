"""Фабрика для создания сессий БД."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import DatabaseConfig


def create_session_factory(config: DatabaseConfig) -> async_sessionmaker[AsyncSession]:
    """Создает фабрику async сессий SQLAlchemy.

    Args:
        config: Конфигурация базы данных.

    Returns:
        Фабрика для создания async сессий.
    """
    db_url = config.get_db_url()
    engine = create_async_engine(
        db_url,
        echo=False,  # Включить для отладки SQL запросов
        pool_pre_ping=True,  # Проверка соединений перед использованием
        pool_size=10,
        max_overflow=20,
    )

    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

