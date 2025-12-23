"""change_agent_actions_entity_id_to_bigint

Revision ID: a3b4c5d6e7f8
Revises: f1a2b3c4d5e6
Create Date: 2025-12-23 11:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3b4c5d6e7f8'
down_revision: Union[str, Sequence[str], None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'agent_actions',
        'entity_id',
        existing_type=sa.Integer(),
        type_=sa.BigInteger(),
        existing_nullable=False,
        existing_comment='ID сущности (например, ID диалога)'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'agent_actions',
        'entity_id',
        existing_type=sa.BigInteger(),
        type_=sa.Integer(),
        existing_nullable=False,
        existing_comment='ID сущности (например, ID диалога)'
    )

