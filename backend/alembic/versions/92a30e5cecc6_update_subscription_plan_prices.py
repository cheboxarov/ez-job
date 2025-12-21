"""update_subscription_plan_prices

Revision ID: 92a30e5cecc6
Revises: 25f4531d764d
Create Date: 2025-12-21 04:14:48.818054

"""
from typing import Sequence, Union
from decimal import Decimal

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92a30e5cecc6'
down_revision: Union[str, Sequence[str], None] = '25f4531d764d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - обновляем цены планов подписки."""
    connection = op.get_bind()
    
    # Обновляем цены планов (вариант 1 - консервативный)
    # PLAN_1: 990 руб/мес
    connection.execute(
        sa.text(
            """
            UPDATE subscription_plans
            SET price = :price
            WHERE name = 'PLAN_1'
            """
        ),
        {"price": Decimal("990.00")}
    )
    
    # PLAN_2: 1990 руб/мес
    connection.execute(
        sa.text(
            """
            UPDATE subscription_plans
            SET price = :price
            WHERE name = 'PLAN_2'
            """
        ),
        {"price": Decimal("1990.00")}
    )
    
    # PLAN_3: 2990 руб/мес
    connection.execute(
        sa.text(
            """
            UPDATE subscription_plans
            SET price = :price
            WHERE name = 'PLAN_3'
            """
        ),
        {"price": Decimal("2990.00")}
    )
    
    # FREE план остается 0 (уже установлено при создании)


def downgrade() -> None:
    """Downgrade schema - возвращаем цены к 0."""
    connection = op.get_bind()
    
    # Возвращаем все платные планы к цене 0
    connection.execute(
        sa.text(
            """
            UPDATE subscription_plans
            SET price = 0
            WHERE name IN ('PLAN_1', 'PLAN_2', 'PLAN_3')
            """
        )
    )
