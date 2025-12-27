"""SQLAlchemy модель пользователя."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB
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

    # HH auth/session data
    hh_user_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hh_headers: Mapped[dict[str, str] | None] = mapped_column(
        JSONB, nullable=True, comment="HH API headers в формате JSON"
    )
    hh_cookies: Mapped[dict[str, str] | None] = mapped_column(
        JSONB, nullable=True, comment="HH API cookies в формате JSON"
    )
    hh_cookies_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Время последнего сохранения hh_cookies/hh_headers в БД (для debounce)",
    )
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)


