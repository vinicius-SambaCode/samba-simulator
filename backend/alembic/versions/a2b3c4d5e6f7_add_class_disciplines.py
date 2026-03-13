"""add_class_disciplines

Revision ID: a2b3c4d5e6f7
Revises: f1a2b3c4d5e6
Create Date: 2026-03-13

Tabela N:N entre school_classes e disciplines.
Permite vincular quais disciplinas pertencem a cada turma.
"""

from alembic import op
import sqlalchemy as sa

revision = 'a2b3c4d5e6f7'
down_revision = 'f1a2b3c4d5e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # IF NOT EXISTS — tabela pode já existir se foi criada manualmente antes desta migration
    op.execute("""
        CREATE TABLE IF NOT EXISTS class_disciplines (
            class_id      INTEGER NOT NULL,
            discipline_id INTEGER NOT NULL,
            PRIMARY KEY (class_id, discipline_id),
            FOREIGN KEY (class_id)      REFERENCES school_classes (id) ON DELETE CASCADE,
            FOREIGN KEY (discipline_id) REFERENCES disciplines (id)    ON DELETE CASCADE
        )
    """)


def downgrade() -> None:
    op.drop_table('class_disciplines')
