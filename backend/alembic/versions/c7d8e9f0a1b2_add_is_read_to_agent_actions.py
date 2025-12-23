"""add_is_read_to_agent_actions

Revision ID: c7d8e9f0a1b2
Revises: a3b4c5d6e7f8
Create Date: 2025-12-23 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c7d8e9f0a1b2"
down_revision: Union[str, Sequence[str], None] = "a3b4c5d6e7f8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "agent_actions",
        sa.Column(
            "is_read",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.create_index(
        op.f("ix_agent_actions_is_read"),
        "agent_actions",
        ["is_read"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_agent_actions_is_read"), table_name="agent_actions")
    op.drop_column("agent_actions", "is_read")


