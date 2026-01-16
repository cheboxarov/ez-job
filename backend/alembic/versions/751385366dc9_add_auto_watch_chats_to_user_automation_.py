from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '751385366dc9'
down_revision: Union[str, Sequence[str], None] = '019b8bd58fcd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('user_automation_settings', sa.Column('auto_watch_chats', sa.Boolean(), server_default='false', nullable=False))

def downgrade() -> None:
    op.drop_column('user_automation_settings', 'auto_watch_chats')
