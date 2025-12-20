"""create_user_hh_auth_data_table

Revision ID: 7a8b9c0d1e2f
Revises: 4da9dcff2a0f
Create Date: 2025-12-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision: str = '7a8b9c0d1e2f'
down_revision: Union[str, Sequence[str], None] = '4da9dcff2a0f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user_hh_auth_data",
        sa.Column("id", UUID(as_uuid=True), nullable=False, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("headers", JSONB, nullable=False, comment="HH API headers в формате JSON"),
        sa.Column("cookies", JSONB, nullable=False, comment="HH API cookies в формате JSON"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", name="uq_user_hh_auth_data_user_id"),
    )
    op.create_index(op.f("ix_user_hh_auth_data_user_id"), "user_hh_auth_data", ["user_id"])


def downgrade() -> None:
    """Downgrade schema."""
    # Проверяем существование индекса перед удалением
    connection = op.get_bind()
    result = connection.execute(
        sa.text("""
            SELECT EXISTS (
                SELECT 1 FROM pg_indexes 
                WHERE indexname = 'ix_user_hh_auth_data_user_id'
            )
        """)
    )
    index_exists = result.scalar()
    if index_exists:
        op.drop_index(op.f("ix_user_hh_auth_data_user_id"), table_name="user_hh_auth_data")
    
    # Проверяем существование таблицы перед удалением
    result = connection.execute(
        sa.text("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'user_hh_auth_data'
            )
        """)
    )
    table_exists = result.scalar()
    if table_exists:
        op.drop_table("user_hh_auth_data")
