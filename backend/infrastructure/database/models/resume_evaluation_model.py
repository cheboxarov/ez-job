"""SQLAlchemy модель оценки резюме."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from infrastructure.database.base import Base


class ResumeEvaluationModel(Base):
    """SQLAlchemy модель оценки резюме.

    Хранит результаты оценки резюме от LLM для кеширования.
    """

    __tablename__ = "resume_evaluations"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    resume_content_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    evaluation_data: Mapped[dict] = mapped_column(JSONB(astext_type=Text()), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)
