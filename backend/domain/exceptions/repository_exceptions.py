"""Исключения для работы с репозиториями."""

from __future__ import annotations


class DuplicateEntityError(Exception):
    """Исключение, которое бросается когда сущность уже существует.

    Используется для абстрагирования от конкретной БД (например, IntegrityError в SQLAlchemy).
    """
    pass
