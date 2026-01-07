"""create_resume_evaluations_table

Revision ID: ad1519588ba5
Revises: 6ff9e21fdeea
Create Date: 2026-01-06 15:10:47.930665

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'ad1519588ba5'
down_revision: Union[str, Sequence[str], None] = '6ff9e21fdeea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'resume_evaluations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('resume_content_hash', sa.String(length=64), nullable=False, comment='SHA256 хеш содержимого резюме'),
        sa.Column('evaluation_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='JSON с результатом оценки: conf, remarks, summary'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_resume_evaluations_resume_content_hash'), 'resume_evaluations', ['resume_content_hash'], unique=True)
    op.create_index(op.f('ix_resume_evaluations_created_at'), 'resume_evaluations', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_resume_evaluations_created_at'), table_name='resume_evaluations')
    op.drop_index(op.f('ix_resume_evaluations_resume_content_hash'), table_name='resume_evaluations')
    op.drop_table('resume_evaluations')
