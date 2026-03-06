"""teacher progress and progress log

Revision ID: a1b2c3d4e5f6
Revises: 6cf7a40b4447
Create Date: 2026-03-06 00:00:00.000000
"""
from __future__ import annotations
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '6cf7a40b4447'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE progressstatusenum AS ENUM ('PENDING', 'PARTIAL', 'COMPLETE');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE progresslogeventenum AS ENUM (
                'QUESTION_ADDED', 'QUESTION_REMOVED',
                'QUOTA_CHANGED', 'STATUS_CHANGED'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    op.create_table(
        "exam_teacher_progress",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("exam_id", sa.Integer(), sa.ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("teacher_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("discipline_id", sa.Integer(), sa.ForeignKey("disciplines.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("class_id", sa.Integer(), sa.ForeignKey("school_classes.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("quota", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("submitted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.Enum("PENDING", "PARTIAL", "COMPLETE", name="progressstatusenum", create_type=False), nullable=False, server_default="PENDING"),
        sa.Column("last_updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.UniqueConstraint("exam_id", "teacher_user_id", "discipline_id", "class_id", name="uq_teacher_progress"),
    )

    op.create_table(
        "exam_progress_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("exam_id", sa.Integer(), sa.ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("teacher_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("discipline_id", sa.Integer(), sa.ForeignKey("disciplines.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("class_id", sa.Integer(), sa.ForeignKey("school_classes.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("event_type", sa.Enum("QUESTION_ADDED", "QUESTION_REMOVED", "QUOTA_CHANGED", "STATUS_CHANGED", name="progresslogeventenum", create_type=False), nullable=False),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("quota_before", sa.Integer(), nullable=True),
        sa.Column("quota_after", sa.Integer(), nullable=True),
        sa.Column("submitted_snap", sa.Integer(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False, index=True),
    )


def downgrade() -> None:
    op.drop_table("exam_progress_log")
    op.drop_table("exam_teacher_progress")
    op.execute("DROP TYPE IF EXISTS progresslogeventenum")
    op.execute("DROP TYPE IF EXISTS progressstatusenum")