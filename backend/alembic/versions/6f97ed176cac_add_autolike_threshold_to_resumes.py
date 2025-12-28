"""add_autolike_threshold_to_resumes

Revision ID: 6f97ed176cac
Revises: e02eb02a19ec
Create Date: 2025-12-28 11:29:16.851655

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f97ed176cac'
down_revision: Union[str, Sequence[str], None] = 'e02eb02a19ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "resumes",
        sa.Column("autolike_threshold", sa.Integer(), nullable=False, server_default=sa.text("50")),
    )
    
    op.execute(
        sa.text("UPDATE resumes SET autolike_threshold = 50 WHERE autolike_threshold IS NULL")
    )
    
    op.create_check_constraint(
        "check_autolike_threshold_range",
        "resumes",
        sa.text("autolike_threshold >= 0 AND autolike_threshold <= 100")
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("check_autolike_threshold_range", "resumes", type_="check")
    op.drop_column("resumes", "autolike_threshold")
