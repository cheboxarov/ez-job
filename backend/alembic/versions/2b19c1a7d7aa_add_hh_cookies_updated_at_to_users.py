"""add_hh_cookies_updated_at_to_users

Revision ID: 2b19c1a7d7aa
Revises: ff01aa23bb45
Create Date: 2025-12-23 18:10:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2b19c1a7d7aa"
down_revision: Union[str, Sequence[str], None] = "ff01aa23bb45"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "hh_cookies_updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Время последнего сохранения hh_cookies/hh_headers в БД (для debounce)",
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "hh_cookies_updated_at")


