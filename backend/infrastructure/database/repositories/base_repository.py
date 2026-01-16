"""Базовый класс для репозиториев с поддержкой двух режимов работы."""

from __future__ import annotations

from abc import ABC
from contextlib import asynccontextmanager
from typing import Awaitable, Callable, TypeVar, Union

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from domain.exceptions.repository_exceptions import DuplicateEntityError


T = TypeVar("T")


class BaseRepository(ABC):
    """Базовый класс для репозиториев с поддержкой двух режимов работы.
    
    Поддерживает два режима:
    1. Транзакционный - использует переданную сессию (для атомарных операций)
    2. Standalone - создает новую сессию на каждый вызов (для независимых операций)
    """

    def __init__(
        self, 
        session_or_factory: Union[AsyncSession, async_sessionmaker[AsyncSession]]
    ) -> None:
        """Инициализация репозитория.
        
        Args:
            session_or_factory: Либо AsyncSession (для транзакционного режима),
                               либо async_sessionmaker (для standalone режима).
        """
        self._session_or_factory = session_or_factory
        self._is_transactional = isinstance(session_or_factory, AsyncSession)
    
    @asynccontextmanager
    async def _get_session(self):
        """Получить сессию в зависимости от режима работы.
        
        В транзакционном режиме возвращает существующую сессию.
        В standalone режиме создает новую сессию на каждый вызов с авто-коммитом.
        
        Yields:
            AsyncSession для работы с БД.
        """
        if self._is_transactional:
            # Транзакционный режим - используем существующую сессию
            yield self._session_or_factory
        else:
            # Standalone режим - создаем новую сессию
            async with self._session_or_factory() as session:
                try:
                    yield session
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise

    async def _execute_with_integrity_handling(
        self, operation: Callable[[], Awaitable[T]]
    ) -> T:
        """Выполнить операцию с обработкой IntegrityError.

        Преобразует SQLAlchemy IntegrityError в доменное исключение DuplicateEntityError.

        Args:
            operation: Асинхронная операция для выполнения.

        Returns:
            Результат операции.

        Raises:
            DuplicateEntityError: При нарушении уникальности.
        """
        try:
            return await operation()
        except IntegrityError as exc:
            raise DuplicateEntityError(str(exc)) from exc
