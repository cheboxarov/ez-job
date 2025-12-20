"""SQLAlchemy модель пользователя."""

from __future__ import annotations

from uuid import UUID

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base import Base


class UserModel(SQLAlchemyBaseUserTableUUID, Base):
    """SQLAlchemy модель пользователя с поддержкой FastAPI Users.

    Наследуется от SQLAlchemyBaseUserTableUUID для получения полей:
    - id (UUID)
    - email (str)
    - hashed_password (str)
    - is_active (bool)
    - is_superuser (bool)
    - is_verified (bool)

    Дополнительно добавляет наши поля:
    - resume_id
    - area
    - salary

    Резюме (resume_text, user_filter_params) вынесены в отдельную таблицу resumes.
    """

    __tablename__ = "users"

    resume_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    area: Mapped[str | None] = mapped_column(String(255), nullable=True)
    salary: Mapped[str | None] = mapped_column(String(255), nullable=True)


