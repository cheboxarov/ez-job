"""create user filter settings

Revision ID: 3d0b1916145b
Revises: 74d3f89af973
Create Date: 2025-12-18 20:16:43.308453

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d0b1916145b'
down_revision: Union[str, Sequence[str], None] = '74d3f89af973'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user_filter_settings",
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("resume_id", sa.String(length=255), nullable=True),
        sa.Column("experience", sa.Text(), nullable=True),
        sa.Column("employment", sa.Text(), nullable=True),
        sa.Column("schedule", sa.Text(), nullable=True),
        sa.Column("professional_role", sa.Text(), nullable=True),
        sa.Column("area", sa.String(length=255), nullable=True),
        sa.Column("salary", sa.Integer(), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("only_with_salary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("order_by", sa.String(length=100), nullable=True),
        sa.Column("period", sa.Integer(), nullable=True),
        sa.Column("date_from", sa.String(length=32), nullable=True),
        sa.Column("date_to", sa.String(length=32), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("user_filter_settings")
