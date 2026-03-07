"""bootstrap roles table

Revision ID: 7fca6166ea07
Revises: e074af2d6c2d
Create Date: 2026-03-06 00:00:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "7fca6166ea07"
down_revision: Union[str, None] = "e074af2d6c2d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=50), nullable=False, unique=True),
    )
    # Se futuras migrations/seed exigirem:
    # op.create_table(
    #     "user_roles",
    #     sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    #     sa.Column("role_id", sa.Integer, sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    # )

def downgrade() -> None:
    # op.drop_table("user_roles")
    op.drop_table("roles")
