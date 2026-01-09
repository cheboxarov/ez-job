"""update_weekly_plan_prices

Revision ID: 019b8bd58fcd
Revises: 7ad1e3eae5dc
Create Date: 2026-01-09 01:31:03.037893

"""
from typing import Sequence, Union
from decimal import Decimal

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '019b8bd58fcd'
down_revision: Union[str, Sequence[str], None] = '7ad1e3eae5dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - обновляем цены планов на неделю (~35% от месячного)."""
    connection = op.get_bind()
    
    # Обновляем цены планов на неделю
    # PLAN_1_WEEK: 350 руб
    connection.execute(
        sa.text(
            """
            UPDATE subscription_plans
            SET price = :price
            WHERE name = 'PLAN_1_WEEK'
            """
        ),
        {"price": Decimal("350.00")}
    )
    
    # PLAN_2_WEEK: 700 руб
    connection.execute(
        sa.text(
            """
            UPDATE subscription_plans
            SET price = :price
            WHERE name = 'PLAN_2_WEEK'
            """
        ),
        {"price": Decimal("700.00")}
    )
    
    # PLAN_3_WEEK: 1050 руб
    connection.execute(
        sa.text(
            """
            UPDATE subscription_plans
            SET price = :price
            WHERE name = 'PLAN_3_WEEK'
            """
        ),
        {"price": Decimal("1050.00")}
    )


def downgrade() -> None:
    """Downgrade schema - возвращаем старые цены (250, 500, 750)."""
    connection = op.get_bind()
    
    # Возвращаем старые цены планов на неделю
    connection.execute(
        sa.text(
            """
            UPDATE subscription_plans
            SET price = :price
            WHERE name = 'PLAN_1_WEEK'
            """
        ),
        {"price": Decimal("250.00")}
    )
    
    connection.execute(
        sa.text(
            """
            UPDATE subscription_plans
            SET price = :price
            WHERE name = 'PLAN_2_WEEK'
            """
        ),
        {"price": Decimal("500.00")}
    )
    
    connection.execute(
        sa.text(
            """
            UPDATE subscription_plans
            SET price = :price
            WHERE name = 'PLAN_3_WEEK'
            """
        ),
        {"price": Decimal("750.00")}
    )
