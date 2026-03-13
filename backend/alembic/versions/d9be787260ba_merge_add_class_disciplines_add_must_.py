"""merge add_class_disciplines + add_must_change_password

Revision ID: d9be787260ba
Revises: e5f6a7b8c9d0, f1a2b3c4d5e6
Create Date: 2026-03-13 00:33:59.807244

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9be787260ba'
down_revision: Union[str, None] = ('e5f6a7b8c9d0', 'f1a2b3c4d5e6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
