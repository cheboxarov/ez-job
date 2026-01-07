"""Фабрика для создания сессий БД."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import DatabaseConfig

_SESSION_FACTORY_CACHE: dict[str, async_sessionmaker[AsyncSession]] = {}
_ENGINE_CACHE: dict[str, object] = {}


def create_session_factory(config: DatabaseConfig) -> async_sessionmaker[AsyncSession]:
    """Создает фабрику async сессий SQLAlchemy.

    Args:
        config: Конфигурация базы данных.

    Returns:
        Фабрика для создания async сессий.
    """
    db_url = config.get_db_url()
    if db_url in _SESSION_FACTORY_CACHE:
        session_factory = _SESSION_FACTORY_CACHE[db_url]
        engine = _ENGINE_CACHE[db_url]
    else:
        engine = create_async_engine(
            db_url,
            echo=False,  # Включить для отладки SQL запросов
            pool_pre_ping=True,  # Проверка соединений перед использованием
            pool_size=20,  # Увеличено с 10 для поддержки большего количества параллельных операций
            max_overflow=30,  # Увеличено с 20, максимум соединений = 50
        )
        session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        _SESSION_FACTORY_CACHE[db_url] = session_factory
        _ENGINE_CACHE[db_url] = engine

    return session_factory

