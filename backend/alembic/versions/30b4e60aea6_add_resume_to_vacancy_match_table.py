"""add_resume_to_vacancy_match_table

Revision ID: 30b4e60aea6
Revises: 95302356f32g
Create Date: 2025-01-27 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '30b4e60aea6'
down_revision: Union[str, Sequence[str], None] = '95302356f32g'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'resume_to_vacancy_matches',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('resume_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('vacancy_hash', sa.String(length=255), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_resume_to_vacancy_matches_resume_id'),
        'resume_to_vacancy_matches',
        ['resume_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_resume_to_vacancy_matches_vacancy_hash'),
        'resume_to_vacancy_matches',
        ['vacancy_hash'],
        unique=False
    )
    op.create_index(
        op.f('ix_resume_to_vacancy_matches_resume_vacancy'),
        'resume_to_vacancy_matches',
        ['resume_id', 'vacancy_hash'],
        unique=True
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f('ix_resume_to_vacancy_matches_resume_vacancy'),
        table_name='resume_to_vacancy_matches'
    )
    op.drop_index(
        op.f('ix_resume_to_vacancy_matches_vacancy_hash'),
        table_name='resume_to_vacancy_matches'
    )
    op.drop_index(
        op.f('ix_resume_to_vacancy_matches_resume_id'),
        table_name='resume_to_vacancy_matches'
    )
    op.drop_table('resume_to_vacancy_matches')
