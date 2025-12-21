"""create_subscription_plans_table

Revision ID: 4cbc2cf266af
Revises: 30b4e60aea6
Create Date: 2025-01-27 15:00:00.000000

"""
from typing import Sequence, Union
from decimal import Decimal
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '4cbc2cf266af'
down_revision: Union[str, Sequence[str], None] = '30b4e60aea6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Создаем таблицу subscription_plans
    op.create_table(
        "subscription_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("response_limit", sa.Integer(), nullable=False),
        sa.Column("reset_period_seconds", sa.Integer(), nullable=False),
        sa.Column("duration_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("price", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.create_index(op.f("ix_subscription_plans_name"), "subscription_plans", ["name"])

    # Вставляем начальные данные
    connection = op.get_bind()
    
    # FREE план: 10 откликов, сброс через 30 дней (2592000 секунд), бессрочно
    free_id = uuid4()
    connection.execute(
        sa.text(
            """
            INSERT INTO subscription_plans (id, name, response_limit, reset_period_seconds, duration_days, price, is_active)
            VALUES (:id, 'FREE', 10, 2592000, 0, 0, true)
            """
        ),
        {"id": free_id}
    )
    
    # PLAN_1: 50 откликов, сброс через 24 часа (86400 секунд), срок 30 дней
    plan1_id = uuid4()
    connection.execute(
        sa.text(
            """
            INSERT INTO subscription_plans (id, name, response_limit, reset_period_seconds, duration_days, price, is_active)
            VALUES (:id, 'PLAN_1', 50, 86400, 30, 0, true)
            """
        ),
        {"id": plan1_id}
    )
    
    # PLAN_2: 100 откликов, сброс через 24 часа, срок 30 дней
    plan2_id = uuid4()
    connection.execute(
        sa.text(
            """
            INSERT INTO subscription_plans (id, name, response_limit, reset_period_seconds, duration_days, price, is_active)
            VALUES (:id, 'PLAN_2', 100, 86400, 30, 0, true)
            """
        ),
        {"id": plan2_id}
    )
    
    # PLAN_3: 200 откликов, сброс через 24 часа, срок 30 дней
    plan3_id = uuid4()
    connection.execute(
        sa.text(
            """
            INSERT INTO subscription_plans (id, name, response_limit, reset_period_seconds, duration_days, price, is_active)
            VALUES (:id, 'PLAN_3', 200, 86400, 30, 0, true)
            """
        ),
        {"id": plan3_id}
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_subscription_plans_name"), table_name="subscription_plans")
    op.drop_table("subscription_plans")
