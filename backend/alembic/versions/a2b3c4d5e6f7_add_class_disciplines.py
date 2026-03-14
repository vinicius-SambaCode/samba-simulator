"""add_class_disciplines

Revision ID: a2b3c4d5e6f7
Revises: f1a2b3c4d5e6
Create Date: 2026-03-13

Tabela N:N entre school_classes e disciplines.
NOTA: a tabela class_disciplines ja e criada pela migration e5f6a7b8c9d0.
Esta migration e mantida apenas para preservar a cadeia de revisoes.
"""

from alembic import op
import sqlalchemy as sa

revision = 'a2b3c4d5e6f7'
down_revision = 'f1a2b3c4d5e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tabela ja criada por e5f6a7b8c9d0 — no-op intencional
    pass


def downgrade() -> None:
    # Nao derruba a tabela pois ela nao foi criada aqui
    pass