"""create_telegram_notification_tables

Revision ID: e02eb02a19ec
Revises: 2b19c1a7d7aa
Create Date: 2025-12-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e02eb02a19ec'
down_revision: Union[str, Sequence[str], None] = '2b19c1a7d7aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'telegram_notification_settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('telegram_chat_id', sa.BigInteger(), nullable=True),
        sa.Column('telegram_username', sa.String(length=255), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('notify_call_request', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('notify_external_action', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('notify_question_answered', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('notify_message_suggestion', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('notify_vacancy_response', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('linked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_telegram_notification_settings_user_id'), 'telegram_notification_settings', ['user_id'], unique=True)
    op.create_index(op.f('ix_telegram_notification_settings_telegram_chat_id'), 'telegram_notification_settings', ['telegram_chat_id'], unique=True)

    op.create_table(
        'telegram_link_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.String(length=64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_telegram_link_tokens_token'), 'telegram_link_tokens', ['token'], unique=True)
    op.create_index(op.f('ix_telegram_link_tokens_user_id'), 'telegram_link_tokens', ['user_id'], unique=False)
    op.create_index(op.f('ix_telegram_link_tokens_expires_at'), 'telegram_link_tokens', ['expires_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_telegram_link_tokens_expires_at'), table_name='telegram_link_tokens')
    op.drop_index(op.f('ix_telegram_link_tokens_user_id'), table_name='telegram_link_tokens')
    op.drop_index(op.f('ix_telegram_link_tokens_token'), table_name='telegram_link_tokens')
    op.drop_table('telegram_link_tokens')
    op.drop_index(op.f('ix_telegram_notification_settings_telegram_chat_id'), table_name='telegram_notification_settings')
    op.drop_index(op.f('ix_telegram_notification_settings_user_id'), table_name='telegram_notification_settings')
    op.drop_table('telegram_notification_settings')
