"""create_llm_calls_table

Revision ID: b2c3d4e5f6a7
Revises: 6f97ed176cac
Create Date: 2025-01-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = '6f97ed176cac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'llm_calls',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('call_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Идентификатор вызова (один для всех попыток одного вызова)'),
        sa.Column('attempt_number', sa.Integer(), nullable=False, comment='Номер попытки (1, 2, 3...)'),
        sa.Column('agent_name', sa.String(length=255), nullable=False, comment='Имя агента (MessagesAgent, VacancyFilterAgent и т.д.)'),
        sa.Column('model', sa.String(length=255), nullable=False, comment='Модель LLM'),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True, comment='ID пользователя'),
        sa.Column('prompt', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='Полный массив messages для промпта'),
        sa.Column('response', sa.Text(), nullable=False, comment='Полный текст ответа от LLM'),
        sa.Column('temperature', sa.Float(), nullable=False, comment='Температура модели'),
        sa.Column('response_format', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Формат ответа (опционально)'),
        sa.Column('status', sa.String(length=50), nullable=False, comment="Статус: 'success' или 'error'"),
        sa.Column('error_type', sa.String(length=255), nullable=True, comment='Тип ошибки (класс исключения)'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='Текст ошибки'),
        sa.Column('duration_ms', sa.Integer(), nullable=True, comment='Время выполнения в миллисекундах'),
        sa.Column('prompt_tokens', sa.Integer(), nullable=True, comment='Количество токенов в промпте'),
        sa.Column('completion_tokens', sa.Integer(), nullable=True, comment='Количество токенов в ответе'),
        sa.Column('total_tokens', sa.Integer(), nullable=True, comment='Общее количество токенов'),
        sa.Column('response_size_bytes', sa.Integer(), nullable=True, comment='Размер ответа в байтах'),
        sa.Column('context', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Дополнительный контекст (use_case, resume_id, vacancy_id, chat_id и т.д.)'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index(op.f('ix_llm_calls_call_id'), 'llm_calls', ['call_id'], unique=False)
    op.create_index(op.f('ix_llm_calls_user_id'), 'llm_calls', ['user_id'], unique=False)
    op.create_index(op.f('ix_llm_calls_created_at'), 'llm_calls', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_llm_calls_created_at'), table_name='llm_calls')
    op.drop_index(op.f('ix_llm_calls_user_id'), table_name='llm_calls')
    op.drop_index(op.f('ix_llm_calls_call_id'), table_name='llm_calls')
    op.drop_table('llm_calls')
