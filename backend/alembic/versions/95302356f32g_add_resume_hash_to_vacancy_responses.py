"""add_resume_hash_to_vacancy_responses

Revision ID: 95302356f32g
Revises: 84291245e21f
Create Date: 2025-01-27 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '95302356f32g'
down_revision: Union[str, Sequence[str], None] = '84291245e21f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "vacancy_responses",
        sa.Column("resume_hash", sa.String(), nullable=True),
    )
    op.create_index(
        op.f("ix_vacancy_responses_resume_hash"),
        "vacancy_responses",
        ["resume_hash"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_vacancy_responses_resume_hash"), table_name="vacancy_responses"
    )
    op.drop_column("vacancy_responses", "resume_hash")
