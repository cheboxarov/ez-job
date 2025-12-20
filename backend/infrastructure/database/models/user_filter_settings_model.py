"""SQLAlchemy‑модель настроек фильтров пользователя."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base import Base


class UserFilterSettingsModel(Base):
    """Настройки фильтров поиска вакансий, привязанные к пользователю.

    Храним ровно одну запись на пользователя (user_id = PK и FK на users.id).
    Списковые поля сериализуются в JSON‑строку на уровне репозитория.
    """

    __tablename__ = "user_filter_settings"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    resume_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    experience: Mapped[str | None] = mapped_column(Text, nullable=True)
    employment: Mapped[str | None] = mapped_column(Text, nullable=True)
    schedule: Mapped[str | None] = mapped_column(Text, nullable=True)
    professional_role: Mapped[str | None] = mapped_column(Text, nullable=True)

    area: Mapped[str | None] = mapped_column(String(255), nullable=True)
    salary: Mapped[int | None] = mapped_column(Integer, nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    only_with_salary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    order_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    period: Mapped[int | None] = mapped_column(Integer, nullable=True)
    date_from: Mapped[str | None] = mapped_column(String(32), nullable=True)
    date_to: Mapped[str | None] = mapped_column(String(32), nullable=True)


