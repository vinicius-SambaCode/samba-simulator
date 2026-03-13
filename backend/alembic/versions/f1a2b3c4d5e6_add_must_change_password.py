"""add_must_change_password

Revision ID: f1a2b3c4d5e6
Revises: d4e5f6a7b8c9
Create Date: 2026-03-13

Adiciona campo must_change_password à tabela users.
Quando True, o sistema exige que o usuário defina uma nova senha no próximo login.
"""

from alembic import op
import sqlalchemy as sa

revision = 'f1a2b3c4d5e6'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column(
            'must_change_password',
            sa.Boolean(),
            nullable=False,
            server_default='false',
        ),
    )


def downgrade() -> None:
    op.drop_column('users', 'must_change_password')
