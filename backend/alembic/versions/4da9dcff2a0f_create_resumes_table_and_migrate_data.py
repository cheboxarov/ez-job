"""create_resumes_table_and_migrate_data

Revision ID: 4da9dcff2a0f
Revises: 3d0b1916145b
Create Date: 2025-12-18 22:34:02.385939

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4da9dcff2a0f'
down_revision: Union[str, Sequence[str], None] = '3d0b1916145b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Создаем таблицу resumes
    op.create_table(
        "resumes",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("user_parameters", sa.Text(), nullable=True),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_resumes_user_id"), "resumes", ["user_id"])

    # 2. Переносим данные из users в resumes
    # Для каждого пользователя с заполненными resume_text или user_filter_params создаем резюме
    connection = op.get_bind()
    
    # Получаем всех пользователей, у которых есть resume_text или user_filter_params
    result = connection.execute(
        sa.text("""
            SELECT id, resume_text, user_filter_params, resume_id
            FROM users
            WHERE resume_text IS NOT NULL 
               OR user_filter_params IS NOT NULL
        """)
    )
    users_data = result.fetchall()

    import uuid
    for user_row in users_data:
        user_id = user_row[0]
        resume_text = user_row[1]  # Может быть None
        user_filter_params = user_row[2]  # Может быть None
        external_id = user_row[3]  # Сохраняем resume_id из users как external_id

        # Нормализуем значения: None -> None, пустая строка -> None
        resume_text_normalized = resume_text.strip() if resume_text else None
        user_filter_params_normalized = user_filter_params.strip() if user_filter_params else None

        # Создаем резюме если есть хотя бы resume_text (не пустая строка)
        # или если есть user_filter_params (даже если resume_text пустой/None)
        if resume_text_normalized:
            # Есть заполненный resume_text
            resume_id = uuid.uuid4()
            connection.execute(
                sa.text("""
                    INSERT INTO resumes (id, user_id, content, user_parameters, external_id)
                    VALUES (:id, :user_id, :content, :user_parameters, :external_id)
                """),
                {
                    "id": resume_id,  # UUID передается напрямую, SQLAlchemy обработает
                    "user_id": user_id,
                    "content": resume_text_normalized,
                    "user_parameters": user_filter_params_normalized,
                    "external_id": external_id,
                }
            )
        elif user_filter_params_normalized:
            # Есть только user_filter_params, создаем резюме с пустым content
            resume_id = uuid.uuid4()
            connection.execute(
                sa.text("""
                    INSERT INTO resumes (id, user_id, content, user_parameters, external_id)
                    VALUES (:id, :user_id, :content, :user_parameters, :external_id)
                """),
                {
                    "id": resume_id,
                    "user_id": user_id,
                    "content": "",  # Пустой content, но есть user_parameters
                    "user_parameters": user_filter_params_normalized,
                    "external_id": external_id,
                }
            )

    # 3. Удаляем колонки resume_text и user_filter_params из users
    op.drop_column("users", "resume_text")
    op.drop_column("users", "user_filter_params")


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Восстанавливаем колонки в users
    op.add_column("users", sa.Column("resume_text", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("user_filter_params", sa.Text(), nullable=True))

    # 2. Переносим данные обратно из resumes в users
    connection = op.get_bind()
    
    # Получаем первое резюме для каждого пользователя (если их несколько)
    result = connection.execute(
        sa.text("""
            SELECT DISTINCT ON (user_id) user_id, content, user_parameters
            FROM resumes
            ORDER BY user_id, id
        """)
    )
    resumes_data = result.fetchall()

    for resume_row in resumes_data:
        user_id = resume_row[0]
        content = resume_row[1] or ""
        user_parameters = resume_row[2]

        # Обновляем пользователя данными из первого резюме
        connection.execute(
            sa.text("""
                UPDATE users
                SET resume_text = :content, user_filter_params = :user_parameters
                WHERE id = :user_id
            """),
            {
                "user_id": user_id,
                "content": content,
                "user_parameters": user_parameters,
            }
        )

    # 3. Удаляем таблицу resumes
    op.drop_index(op.f("ix_resumes_user_id"), table_name="resumes")
    op.drop_table("resumes")
