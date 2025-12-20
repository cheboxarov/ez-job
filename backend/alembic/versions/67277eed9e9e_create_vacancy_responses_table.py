"""create_vacancy_responses_table

Revision ID: 67277eed9e9e
Revises: e7f8g9h0i1j2
Create Date: 2025-01-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '67277eed9e9e'
down_revision: Union[str, Sequence[str], None] = 'e7f8g9h0i1j2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "vacancy_responses",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column("vacancy_id", sa.Integer(), nullable=False),
        sa.Column("resume_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cover_letter", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_vacancy_responses_vacancy_id"), "vacancy_responses", ["vacancy_id"])
    op.create_index(op.f("ix_vacancy_responses_resume_id"), "vacancy_responses", ["resume_id"])
    op.create_index(op.f("ix_vacancy_responses_user_id"), "vacancy_responses", ["user_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_vacancy_responses_user_id"), table_name="vacancy_responses")
    op.drop_index(op.f("ix_vacancy_responses_resume_id"), table_name="vacancy_responses")
    op.drop_index(op.f("ix_vacancy_responses_vacancy_id"), table_name="vacancy_responses")
    op.drop_table("vacancy_responses")
