"""SQLAlchemy модель мэтча резюме-вакансия."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base import Base


class ResumeToVacancyMatchModel(Base):
    """SQLAlchemy модель мэтча резюме-вакансия.

    Хранит результаты нейронной фильтрации вакансий для резюме.
    """

    __tablename__ = "resume_to_vacancy_matches"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    resume_id: Mapped[UUID] = mapped_column(
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vacancy_hash: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index(
            "ix_resume_to_vacancy_matches_resume_vacancy",
            "resume_id",
            "vacancy_hash",
            unique=True,
        ),
    )
