"""add_cost_usd_to_llm_calls

Revision ID: 6ff9e21fdeea
Revises: a59fb1b36e61
Create Date: 2026-01-06 19:25:04.805564

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ff9e21fdeea'
down_revision: Union[str, Sequence[str], None] = 'a59fb1b36e61'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'llm_calls',
        sa.Column('cost_usd', sa.Float(), nullable=True, comment='Стоимость вызова в USD'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('llm_calls', 'cost_usd')
