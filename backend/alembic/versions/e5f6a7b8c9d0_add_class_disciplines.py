"""add_class_disciplines

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-03-11

Cria a tabela class_disciplines que define a grade curricular formal
de cada turma: quais disciplinas fazem parte do currículo de cada SchoolClass.
"""
from alembic import op
import sqlalchemy as sa
from typing import Union

revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'class_disciplines',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('class_id', sa.Integer(),
                  sa.ForeignKey('school_classes.id', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.Column('discipline_id', sa.Integer(),
                  sa.ForeignKey('disciplines.id', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.UniqueConstraint('class_id', 'discipline_id', name='uq_class_discipline'),
    )


def downgrade() -> None:
    op.drop_table('class_disciplines')
