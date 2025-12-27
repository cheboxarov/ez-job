"""move_hh_auth_data_to_users

Revision ID: ff01aa23bb45
Revises: c7d8e9f0a1b2
Create Date: 2025-12-23 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "ff01aa23bb45"
down_revision: Union[str, Sequence[str], None] = "c7d8e9f0a1b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: перенести HH auth данные в таблицу users и удалить user_hh_auth_data."""
    # 1. Новые колонки в users
    op.add_column("users", sa.Column("hh_user_id", sa.String(length=255), nullable=True))
    op.add_column(
        "users",
        sa.Column(
            "hh_headers",
            postgresql.JSONB(astext_type=sa.Text()),  # type: ignore[arg-type]
            nullable=True,
            comment="HH API headers в формате JSON",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "hh_cookies",
            postgresql.JSONB(astext_type=sa.Text()),  # type: ignore[arg-type]
            nullable=True,
            comment="HH API cookies в формате JSON",
        ),
    )
    op.add_column("users", sa.Column("phone", sa.String(length=32), nullable=True))

    # Уникальный индекс по hh_user_id (NULL значения допускаются)
    op.create_index(
        op.f("ix_users_hh_user_id"),
        "users",
        ["hh_user_id"],
        unique=True,
    )

    # 2. Перенос данных из user_hh_auth_data в users
    # Берём headers/cookies и вытаскиваем hh_user_id из cookies->>'hhuid'
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            UPDATE users AS u
            SET
                hh_headers = a.headers,
                hh_cookies = a.cookies,
                hh_user_id = COALESCE(a.cookies->>'hhuid', u.hh_user_id)
            FROM user_hh_auth_data AS a
            WHERE a.user_id = u.id
            """
        )
    )
    # phone для существующих пользователей оставляем NULL — ты сам потом заполнишь, если нужно

    # 3. Удаляем индекс и таблицу user_hh_auth_data, если они существуют
    # (логика похожа на 7a8b9c0d1e2f_create_user_hh_auth_data_table.py)
    result = conn.execute(
        sa.text(
            """
            SELECT EXISTS (
                SELECT 1 FROM pg_indexes
                WHERE indexname = 'ix_user_hh_auth_data_user_id'
            )
            """
        )
    )
    index_exists = result.scalar()
    if index_exists:
        op.drop_index(
            op.f("ix_user_hh_auth_data_user_id"),
            table_name="user_hh_auth_data",
        )

    result = conn.execute(
        sa.text(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = 'user_hh_auth_data'
            )
            """
        )
    )
    table_exists = result.scalar()
    if table_exists:
        op.drop_table("user_hh_auth_data")


def downgrade() -> None:
    """Downgrade schema: создать user_hh_auth_data заново и вернуть данные из users."""
    conn = op.get_bind()

    # 1. Восстанавливаем таблицу user_hh_auth_data (структура как в 7a8b9c0d1e2f)
    op.create_table(
        "user_hh_auth_data",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "headers",
            postgresql.JSONB(astext_type=sa.Text()),  # type: ignore[arg-type]
            nullable=False,
            comment="HH API headers в формате JSON",
        ),
        sa.Column(
            "cookies",
            postgresql.JSONB(astext_type=sa.Text()),  # type: ignore[arg-type]
            nullable=False,
            comment="HH API cookies в формате JSON",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", name="uq_user_hh_auth_data_user_id"),
    )
    op.create_index(
        op.f("ix_user_hh_auth_data_user_id"),
        "user_hh_auth_data",
        ["user_id"],
    )

    # 2. Переносим данные обратно из users, только где есть hh_cookies/hh_headers
    conn.execute(
        sa.text(
            """
            INSERT INTO user_hh_auth_data (user_id, headers, cookies)
            SELECT id, hh_headers, hh_cookies
            FROM users
            WHERE hh_headers IS NOT NULL AND hh_cookies IS NOT NULL
            """
        )
    )

    # 3. Удаляем колонки из users
    op.drop_index(op.f("ix_users_hh_user_id"), table_name="users")
    op.drop_column("users", "phone")
    op.drop_column("users", "hh_cookies")
    op.drop_column("users", "hh_headers")
    op.drop_column("users", "hh_user_id")


