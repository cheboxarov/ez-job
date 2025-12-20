"""rename_user_filter_settings_to_resume_filter_settings

Revision ID: daf2e352ac7d
Revises: 7a8b9c0d1e2f
Create Date: 2025-12-18 22:48:36.508480

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'daf2e352ac7d'
down_revision: Union[str, Sequence[str], None] = '7a8b9c0d1e2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Создаем таблицу resume_filter_settings
    op.create_table(
        "resume_filter_settings",
        sa.Column("resume_id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("hh_resume_id", sa.String(length=255), nullable=True),
        sa.Column("experience", sa.Text(), nullable=True),
        sa.Column("employment", sa.Text(), nullable=True),
        sa.Column("schedule", sa.Text(), nullable=True),
        sa.Column("professional_role", sa.Text(), nullable=True),
        sa.Column("area", sa.String(length=255), nullable=True),
        sa.Column("salary", sa.Integer(), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("only_with_salary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("order_by", sa.String(length=100), nullable=True),
        sa.Column("period", sa.Integer(), nullable=True),
        sa.Column("date_from", sa.String(length=32), nullable=True),
        sa.Column("date_to", sa.String(length=32), nullable=True),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
    )

    # 2. Переносим данные из user_filter_settings в resume_filter_settings
    connection = op.get_bind()
    
    # Получаем все записи из user_filter_settings
    result = connection.execute(
        sa.text("""
            SELECT user_id, text, resume_id, experience, employment, schedule,
                   professional_role, area, salary, currency, only_with_salary,
                   order_by, period, date_from, date_to
            FROM user_filter_settings
        """)
    )
    settings_data = result.fetchall()

    import uuid
    for setting_row in settings_data:
        user_id = setting_row[0]
        text = setting_row[1]
        hh_resume_id = setting_row[2]  # Это старый resume_id (HH ID)
        experience = setting_row[3]
        employment = setting_row[4]
        schedule = setting_row[5]
        professional_role = setting_row[6]
        area = setting_row[7]
        salary = setting_row[8]
        currency = setting_row[9]
        only_with_salary = setting_row[10]
        order_by = setting_row[11]
        period = setting_row[12]
        date_from = setting_row[13]
        date_to = setting_row[14]

        # Находим первое резюме пользователя
        resume_result = connection.execute(
            sa.text("""
                SELECT id FROM resumes
                WHERE user_id = :user_id
                ORDER BY id
                LIMIT 1
            """),
            {"user_id": user_id}
        )
        resume_row = resume_result.fetchone()

        if resume_row is None:
            # Если резюме нет, создаем пустое резюме
            resume_id = uuid.uuid4()
            connection.execute(
                sa.text("""
                    INSERT INTO resumes (id, user_id, content, user_parameters, external_id)
                    VALUES (:id, :user_id, :content, :user_parameters, :external_id)
                """),
                {
                    "id": resume_id,
                    "user_id": user_id,
                    "content": "",
                    "user_parameters": None,
                    "external_id": None,
                }
            )
        else:
            resume_id = resume_row[0]

        # Вставляем настройки фильтров для резюме
        connection.execute(
            sa.text("""
                INSERT INTO resume_filter_settings (
                    resume_id, text, hh_resume_id, experience, employment, schedule,
                    professional_role, area, salary, currency, only_with_salary,
                    order_by, period, date_from, date_to
                )
                VALUES (
                    :resume_id, :text, :hh_resume_id, :experience, :employment, :schedule,
                    :professional_role, :area, :salary, :currency, :only_with_salary,
                    :order_by, :period, :date_from, :date_to
                )
            """),
            {
                "resume_id": resume_id,
                "text": text,
                "hh_resume_id": hh_resume_id,
                "experience": experience,
                "employment": employment,
                "schedule": schedule,
                "professional_role": professional_role,
                "area": area,
                "salary": salary,
                "currency": currency,
                "only_with_salary": only_with_salary,
                "order_by": order_by,
                "period": period,
                "date_from": date_from,
                "date_to": date_to,
            }
        )

    # 3. Удаляем старую таблицу user_filter_settings
    op.drop_table("user_filter_settings")


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Восстанавливаем таблицу user_filter_settings
    op.create_table(
        "user_filter_settings",
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("resume_id", sa.String(length=255), nullable=True),
        sa.Column("experience", sa.Text(), nullable=True),
        sa.Column("employment", sa.Text(), nullable=True),
        sa.Column("schedule", sa.Text(), nullable=True),
        sa.Column("professional_role", sa.Text(), nullable=True),
        sa.Column("area", sa.String(length=255), nullable=True),
        sa.Column("salary", sa.Integer(), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("only_with_salary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("order_by", sa.String(length=100), nullable=True),
        sa.Column("period", sa.Integer(), nullable=True),
        sa.Column("date_from", sa.String(length=32), nullable=True),
        sa.Column("date_to", sa.String(length=32), nullable=True),
    )

    # 2. Переносим данные обратно из resume_filter_settings в user_filter_settings
    connection = op.get_bind()
    
    # Получаем все записи из resume_filter_settings с user_id из резюме
    result = connection.execute(
        sa.text("""
            SELECT r.user_id, rfs.text, rfs.hh_resume_id, rfs.experience, rfs.employment,
                   rfs.schedule, rfs.professional_role, rfs.area, rfs.salary, rfs.currency,
                   rfs.only_with_salary, rfs.order_by, rfs.period, rfs.date_from, rfs.date_to
            FROM resume_filter_settings rfs
            JOIN resumes r ON rfs.resume_id = r.id
            ORDER BY r.user_id, rfs.resume_id
        """)
    )
    settings_data = result.fetchall()

    for setting_row in settings_data:
        user_id = setting_row[0]
        text = setting_row[1]
        resume_id = setting_row[2]  # hh_resume_id -> resume_id в старой таблице
        experience = setting_row[3]
        employment = setting_row[4]
        schedule = setting_row[5]
        professional_role = setting_row[6]
        area = setting_row[7]
        salary = setting_row[8]
        currency = setting_row[9]
        only_with_salary = setting_row[10]
        order_by = setting_row[11]
        period = setting_row[12]
        date_from = setting_row[13]
        date_to = setting_row[14]

        # Берем первую запись для каждого пользователя (если их несколько)
        # Используем INSERT ... ON CONFLICT DO NOTHING или проверку существования
        connection.execute(
            sa.text("""
                INSERT INTO user_filter_settings (
                    user_id, text, resume_id, experience, employment, schedule,
                    professional_role, area, salary, currency, only_with_salary,
                    order_by, period, date_from, date_to
                )
                VALUES (
                    :user_id, :text, :resume_id, :experience, :employment, :schedule,
                    :professional_role, :area, :salary, :currency, :only_with_salary,
                    :order_by, :period, :date_from, :date_to
                )
                ON CONFLICT (user_id) DO NOTHING
            """),
            {
                "user_id": user_id,
                "text": text,
                "resume_id": resume_id,
                "experience": experience,
                "employment": employment,
                "schedule": schedule,
                "professional_role": professional_role,
                "area": area,
                "salary": salary,
                "currency": currency,
                "only_with_salary": only_with_salary,
                "order_by": order_by,
                "period": period,
                "date_from": date_from,
                "date_to": date_to,
            }
        )

    # 3. Удаляем таблицу resume_filter_settings
    op.drop_table("resume_filter_settings")
