"""add_vacancy_name_and_url_to_vacancy_responses

Revision ID: 84291245e21f
Revises: 67277eed9e9e
Create Date: 2025-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '84291245e21f'
down_revision: Union[str, Sequence[str], None] = '67277eed9e9e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "vacancy_responses",
        sa.Column("vacancy_name", sa.String(), nullable=False, server_default=""),
    )
    op.add_column(
        "vacancy_responses",
        sa.Column("vacancy_url", sa.String(), nullable=True),
    )
    # Убираем server_default после добавления колонки, если нужно
    op.alter_column("vacancy_responses", "vacancy_name", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("vacancy_responses", "vacancy_url")
    op.drop_column("vacancy_responses", "vacancy_name")
