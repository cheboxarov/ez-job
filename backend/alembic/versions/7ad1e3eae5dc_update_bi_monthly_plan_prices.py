"""update_bi_monthly_plan_prices

Revision ID: 7ad1e3eae5dc
Revises: f15ee1732fdb
Create Date: 2026-01-09 01:19:54.924820

"""
from typing import Sequence, Union
from decimal import Decimal

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ad1e3eae5dc'
down_revision: Union[str, Sequence[str], None] = 'f15ee1732fdb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - обновляем цены планов на 2 месяца."""
    connection = op.get_bind()
    
    # Обновляем цены планов на 2 месяца
    # PLAN_1_2MONTHS: 1800 руб
    connection.execute(
        sa.text(
            """
            UPDATE subscription_plans
            SET price = :price
            WHERE name = 'PLAN_1_2MONTHS'
            """
        ),
        {"price": Decimal("1800.00")}
    )
    
    # PLAN_2_2MONTHS: 3600 руб
    connection.execute(
        sa.text(
            """
            UPDATE subscription_plans
            SET price = :price
            WHERE name = 'PLAN_2_2MONTHS'
            """
        ),
        {"price": Decimal("3600.00")}
    )
    
    # PLAN_3_2MONTHS: 5400 руб
    connection.execute(
        sa.text(
            """
            UPDATE subscription_plans
            SET price = :price
            WHERE name = 'PLAN_3_2MONTHS'
            """
        ),
        {"price": Decimal("5400.00")}
    )


def downgrade() -> None:
    """Downgrade schema - возвращаем старые цены (1782, 3582, 5382)."""
    connection = op.get_bind()
    
    # Возвращаем старые цены планов на 2 месяца
    connection.execute(
        sa.text(
            """
            UPDATE subscription_plans
            SET price = :price
            WHERE name = 'PLAN_1_2MONTHS'
            """
        ),
        {"price": Decimal("1782.00")}
    )
    
    connection.execute(
        sa.text(
            """
            UPDATE subscription_plans
            SET price = :price
            WHERE name = 'PLAN_2_2MONTHS'
            """
        ),
        {"price": Decimal("3582.00")}
    )
    
    connection.execute(
        sa.text(
            """
            UPDATE subscription_plans
            SET price = :price
            WHERE name = 'PLAN_3_2MONTHS'
            """
        ),
        {"price": Decimal("5382.00")}
    )
