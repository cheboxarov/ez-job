"""create_user_subscriptions_table

Revision ID: 25f4531d764d
Revises: 4cbc2cf266af
Create Date: 2025-01-27 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '25f4531d764d'
down_revision: Union[str, Sequence[str], None] = '4cbc2cf266af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Создаем таблицу user_subscriptions
    op.create_table(
        "user_subscriptions",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column("subscription_plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("responses_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("period_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["subscription_plan_id"], ["subscription_plans.id"], ondelete="RESTRICT"),
    )
    op.create_index(op.f("ix_user_subscriptions_subscription_plan_id"), "user_subscriptions", ["subscription_plan_id"])

    # Создаем записи для существующих пользователей с FREE планом
    connection = op.get_bind()
    
    # Получаем ID FREE плана
    result = connection.execute(
        sa.text("SELECT id FROM subscription_plans WHERE name = 'FREE' LIMIT 1")
    )
    free_plan_row = result.fetchone()
    
    if free_plan_row:
        free_plan_id = free_plan_row[0]
        
        # Создаем подписки для всех существующих пользователей
        connection.execute(
            sa.text(
                """
                INSERT INTO user_subscriptions (user_id, subscription_plan_id, responses_count, period_started_at, started_at, expires_at)
                SELECT id, :free_plan_id, 0, NULL, NOW(), NULL
                FROM users
                WHERE id NOT IN (SELECT user_id FROM user_subscriptions)
                """
            ),
            {"free_plan_id": free_plan_id}
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_user_subscriptions_subscription_plan_id"), table_name="user_subscriptions")
    op.drop_table("user_subscriptions")
