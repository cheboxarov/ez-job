"""add_error_fields_to_vacancy_responses

Revision ID: 341b7991e4d6
Revises: ad1519588ba5
Create Date: 2026-01-07 19:29:42.620945

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '341b7991e4d6'
down_revision: Union[str, Sequence[str], None] = 'ad1519588ba5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Добавляем поле status с default='success'
    op.add_column(
        "vacancy_responses",
        sa.Column("status", sa.String(), nullable=False, server_default="success"),
    )
    
    # Добавляем поле error_status_code (nullable)
    op.add_column(
        "vacancy_responses",
        sa.Column("error_status_code", sa.Integer(), nullable=True),
    )
    
    # Добавляем поле error_message (nullable)
    op.add_column(
        "vacancy_responses",
        sa.Column("error_message", sa.Text(), nullable=True),
    )
    
    # Создаем составной индекс на (resume_id, vacancy_id, status) для быстрой проверки неудачных откликов
    op.create_index(
        "ix_vacancy_responses_resume_vacancy_status",
        "vacancy_responses",
        ["resume_id", "vacancy_id", "status"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем индекс
    op.drop_index(
        "ix_vacancy_responses_resume_vacancy_status",
        table_name="vacancy_responses",
    )
    
    # Удаляем колонки
    op.drop_column("vacancy_responses", "error_message")
    op.drop_column("vacancy_responses", "error_status_code")
    op.drop_column("vacancy_responses", "status")
