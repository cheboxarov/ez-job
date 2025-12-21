"""SQLAlchemy модель плана подписки."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base import Base


class SubscriptionPlanModel(Base):
    """SQLAlchemy модель плана подписки.

    Справочник тарифов с лимитами откликов и периодами восстановления.
    """

    __tablename__ = "subscription_plans"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    response_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    reset_period_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
