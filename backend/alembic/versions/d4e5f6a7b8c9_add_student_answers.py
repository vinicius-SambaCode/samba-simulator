"""add_student_answers

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-03-09

Tabela student_answers para armazenar respostas lidas via OMR scanner.
"""

from alembic import op

revision = 'd4e5f6a7b8c9'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS student_answers (
            id                  SERIAL PRIMARY KEY,
            exam_id             INTEGER NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
            student_id          INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
            question_link_id    INTEGER NOT NULL REFERENCES exam_question_link(id) ON DELETE CASCADE,
            marked_label        VARCHAR(1),
            is_correct          BOOLEAN,
            scanned_at          TIMESTAMP DEFAULT NOW(),
            UNIQUE (exam_id, student_id, question_link_id)
        );
        CREATE INDEX IF NOT EXISTS ix_student_answers_exam_student
            ON student_answers(exam_id, student_id);
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS student_answers;")
