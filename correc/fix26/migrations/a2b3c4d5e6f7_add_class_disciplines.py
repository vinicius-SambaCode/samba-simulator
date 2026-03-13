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
    op.create_table(
        'class_disciplines',
        sa.Column('class_id',      sa.Integer(), nullable=False),
        sa.Column('discipline_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['class_id'],      ['school_classes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['discipline_id'], ['disciplines.id'],    ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('class_id', 'discipline_id'),
    )


def downgrade() -> None:
    op.drop_table('class_disciplines')
