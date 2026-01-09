"""add_weekly_and_bi_monthly_plans

Revision ID: f15ee1732fdb
Revises: 341b7991e4d6
Create Date: 2026-01-09 00:03:54.251035

"""
from typing import Sequence, Union
from decimal import Decimal
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f15ee1732fdb'
down_revision: Union[str, Sequence[str], None] = '341b7991e4d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - добавляем планы на неделю и 2 месяца, переименовываем месячные."""
    connection = op.get_bind()
    
    # Переименовываем существующие месячные планы
    connection.execute(
        sa.text(
            """
            UPDATE subscription_plans
            SET name = 'PLAN_1_MONTH'
            WHERE name = 'PLAN_1'
            """
        )
    )
    
    connection.execute(
        sa.text(
            """
            UPDATE subscription_plans
            SET name = 'PLAN_2_MONTH'
            WHERE name = 'PLAN_2'
            """
        )
    )
    
    connection.execute(
        sa.text(
            """
            UPDATE subscription_plans
            SET name = 'PLAN_3_MONTH'
            WHERE name = 'PLAN_3'
            """
        )
    )
    
    # Создаем планы на неделю (7 дней)
    plan1_week_id = uuid4()
    connection.execute(
        sa.text(
            """
            INSERT INTO subscription_plans (id, name, response_limit, reset_period_seconds, duration_days, price, is_active)
            VALUES (:id, 'PLAN_1_WEEK', 50, 86400, 7, :price, true)
            """
        ),
        {"id": plan1_week_id, "price": Decimal("250.00")}
    )
    
    plan2_week_id = uuid4()
    connection.execute(
        sa.text(
            """
            INSERT INTO subscription_plans (id, name, response_limit, reset_period_seconds, duration_days, price, is_active)
            VALUES (:id, 'PLAN_2_WEEK', 100, 86400, 7, :price, true)
            """
        ),
        {"id": plan2_week_id, "price": Decimal("500.00")}
    )
    
    plan3_week_id = uuid4()
    connection.execute(
        sa.text(
            """
            INSERT INTO subscription_plans (id, name, response_limit, reset_period_seconds, duration_days, price, is_active)
            VALUES (:id, 'PLAN_3_WEEK', 200, 86400, 7, :price, true)
            """
        ),
        {"id": plan3_week_id, "price": Decimal("750.00")}
    )
    
    # Создаем планы на 2 месяца (60 дней)
    plan1_2months_id = uuid4()
    connection.execute(
        sa.text(
            """
            INSERT INTO subscription_plans (id, name, response_limit, reset_period_seconds, duration_days, price, is_active)
            VALUES (:id, 'PLAN_1_2MONTHS', 50, 86400, 60, :price, true)
            """
        ),
        {"id": plan1_2months_id, "price": Decimal("1782.00")}
    )
    
    plan2_2months_id = uuid4()
    connection.execute(
        sa.text(
            """
            INSERT INTO subscription_plans (id, name, response_limit, reset_period_seconds, duration_days, price, is_active)
            VALUES (:id, 'PLAN_2_2MONTHS', 100, 86400, 60, :price, true)
            """
        ),
        {"id": plan2_2months_id, "price": Decimal("3582.00")}
    )
    
    plan3_2months_id = uuid4()
    connection.execute(
        sa.text(
            """
            INSERT INTO subscription_plans (id, name, response_limit, reset_period_seconds, duration_days, price, is_active)
            VALUES (:id, 'PLAN_3_2MONTHS', 200, 86400, 60, :price, true)
            """
        ),
        {"id": plan3_2months_id, "price": Decimal("5382.00")}
    )


def downgrade() -> None:
    """Downgrade schema - удаляем новые планы и возвращаем старые названия."""
    connection = op.get_bind()
    
    # Удаляем планы на неделю
    connection.execute(
        sa.text(
            """
            DELETE FROM subscription_plans
            WHERE name IN ('PLAN_1_WEEK', 'PLAN_2_WEEK', 'PLAN_3_WEEK')
            """
        )
    )
    
    # Удаляем планы на 2 месяца
    connection.execute(
        sa.text(
            """
            DELETE FROM subscription_plans
            WHERE name IN ('PLAN_1_2MONTHS', 'PLAN_2_2MONTHS', 'PLAN_3_2MONTHS')
            """
        )
    )
    
    # Возвращаем старые названия месячных планов
    connection.execute(
        sa.text(
            """
            UPDATE subscription_plans
            SET name = 'PLAN_1'
            WHERE name = 'PLAN_1_MONTH'
            """
        )
    )
    
    connection.execute(
        sa.text(
            """
            UPDATE subscription_plans
            SET name = 'PLAN_2'
            WHERE name = 'PLAN_2_MONTH'
            """
        )
    )
    
    connection.execute(
        sa.text(
            """
            UPDATE subscription_plans
            SET name = 'PLAN_3'
            WHERE name = 'PLAN_3_MONTH'
            """
        )
    )
