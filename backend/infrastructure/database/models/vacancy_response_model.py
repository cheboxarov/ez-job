"""SQLAlchemy модель отклика на вакансию."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Text, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from infrastructure.database.base import Base


class VacancyResponseModel(Base):
    """SQLAlchemy модель отклика на вакансию.

    Хранит информацию об откликах пользователей на вакансии через HeadHunter.
    """

    __tablename__ = "vacancy_responses"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    vacancy_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    resume_id: Mapped[UUID] = mapped_column(
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    resume_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cover_letter: Mapped[str] = mapped_column(Text, nullable=False)
    vacancy_name: Mapped[str] = mapped_column(String, nullable=False)
    vacancy_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
