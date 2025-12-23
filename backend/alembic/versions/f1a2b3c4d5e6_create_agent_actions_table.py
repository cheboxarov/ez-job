"""create_agent_actions_table

Revision ID: f1a2b3c4d5e6
Revises: 92a30e5cecc6
Create Date: 2025-12-23 11:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = '92a30e5cecc6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'agent_actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('type', sa.String(length=255), nullable=False, comment='Тип действия (send_message, create_event и т.д.)'),
        sa.Column('entity_type', sa.String(length=255), nullable=False, comment='Тип сущности (hh_dialog и т.д.)'),
        sa.Column('entity_id', sa.Integer(), nullable=False, comment='ID сущности (например, ID диалога)'),
        sa.Column('created_by', sa.String(length=255), nullable=False, comment='Идентификатор агента, создавшего действие'),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID пользователя, для которого создано действие'),
        sa.Column('resume_hash', sa.String(length=255), nullable=True, comment='Hash резюме, использованного при создании действия'),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='JSON данные действия (зависят от типа действия)'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_actions_type'), 'agent_actions', ['type'], unique=False)
    op.create_index(op.f('ix_agent_actions_entity_type'), 'agent_actions', ['entity_type'], unique=False)
    op.create_index(op.f('ix_agent_actions_entity_id'), 'agent_actions', ['entity_id'], unique=False)
    op.create_index(op.f('ix_agent_actions_created_by'), 'agent_actions', ['created_by'], unique=False)
    op.create_index(op.f('ix_agent_actions_user_id'), 'agent_actions', ['user_id'], unique=False)
    op.create_index(op.f('ix_agent_actions_resume_hash'), 'agent_actions', ['resume_hash'], unique=False)
    op.create_index(op.f('ix_agent_actions_created_at'), 'agent_actions', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_agent_actions_created_at'), table_name='agent_actions')
    op.drop_index(op.f('ix_agent_actions_resume_hash'), table_name='agent_actions')
    op.drop_index(op.f('ix_agent_actions_user_id'), table_name='agent_actions')
    op.drop_index(op.f('ix_agent_actions_created_by'), table_name='agent_actions')
    op.drop_index(op.f('ix_agent_actions_entity_id'), table_name='agent_actions')
    op.drop_index(op.f('ix_agent_actions_entity_type'), table_name='agent_actions')
    op.drop_index(op.f('ix_agent_actions_type'), table_name='agent_actions')
    op.drop_table('agent_actions')

