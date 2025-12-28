"""SQLAlchemy модель резюме."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base import Base


class ResumeModel(Base):
    """SQLAlchemy модель резюме.

    Хранит резюме пользователя с текстом и дополнительными параметрами.
    """

    __tablename__ = "resumes"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_parameters: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    headhunter_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_auto_reply: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    autolike_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=50)