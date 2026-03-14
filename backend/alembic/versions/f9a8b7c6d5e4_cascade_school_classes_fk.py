"""add cascade delete to school_classes foreign keys

Revision ID: f9a8b7c6d5e4
Revises: aabbcc112233
Create Date: 2026-03-14

Adiciona ON DELETE CASCADE nas FKs que referenciam school_classes,
permitindo excluir turmas sem violar constraints de integridade.

Tabelas: exam_class_assignment, exam_teacher_assignment,
         teacher_class_subject, questions, students
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision = 'f9a8b7c6d5e4'
down_revision = 'aabbcc112233'
branch_labels = None
depends_on = None


def _get_fk_name(conn, table: str, column: str) -> str | None:
    """Descobre o nome real da FK constraint no banco (independente de convenção)."""
    result = conn.execute(text("""
        SELECT tc.constraint_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
          AND tc.table_schema = kcu.table_schema
        JOIN information_schema.referential_constraints AS rc
          ON tc.constraint_name = rc.constraint_name
          AND tc.table_schema = rc.constraint_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_name = :table
          AND kcu.column_name = :column
          AND tc.table_schema = 'public'
    """), {"table": table, "column": column})
    row = result.fetchone()
    return row[0] if row else None


def _recreate_fk_cascade(conn, table: str, col: str, new_name: str) -> None:
    """Remove a FK existente (qualquer que seja o nome) e recria com CASCADE."""
    old_name = _get_fk_name(conn, table, col)
    if old_name:
        conn.execute(text(f'ALTER TABLE {table} DROP CONSTRAINT "{old_name}"'))
    conn.execute(text(
        f'ALTER TABLE {table} ADD CONSTRAINT "{new_name}" '
        f'FOREIGN KEY ({col}) REFERENCES school_classes (id) ON DELETE CASCADE'
    ))


def _restore_fk_plain(conn, table: str, col: str, cascade_name: str, plain_name: str) -> None:
    """Reverte para FK sem CASCADE (downgrade)."""
    conn.execute(text(f'ALTER TABLE {table} DROP CONSTRAINT IF EXISTS "{cascade_name}"'))
    conn.execute(text(
        f'ALTER TABLE {table} ADD CONSTRAINT "{plain_name}" '
        f'FOREIGN KEY ({col}) REFERENCES school_classes (id)'
    ))


def upgrade() -> None:
    conn = op.get_bind()
    _recreate_fk_cascade(conn, 'exam_class_assignment',   'class_id', 'fk_exam_class_asgn_class_cascade')
    _recreate_fk_cascade(conn, 'exam_teacher_assignment', 'class_id', 'fk_exam_teacher_asgn_class_cascade')
    _recreate_fk_cascade(conn, 'teacher_class_subject',   'class_id', 'fk_teacher_class_subj_cascade')
    _recreate_fk_cascade(conn, 'questions',               'class_id', 'fk_questions_class_cascade')
    _recreate_fk_cascade(conn, 'students',                'class_id', 'fk_students_class_cascade')


def downgrade() -> None:
    conn = op.get_bind()
    _restore_fk_plain(conn, 'exam_class_assignment',   'class_id', 'fk_exam_class_asgn_class_cascade',    'exam_class_assignment_class_id_fkey')
    _restore_fk_plain(conn, 'exam_teacher_assignment', 'class_id', 'fk_exam_teacher_asgn_class_cascade',  'exam_teacher_assignment_class_id_fkey')
    _restore_fk_plain(conn, 'teacher_class_subject',   'class_id', 'fk_teacher_class_subj_cascade',       'teacher_class_subject_class_id_fkey')
    _restore_fk_plain(conn, 'questions',               'class_id', 'fk_questions_class_cascade',          'questions_class_id_fkey')
    _restore_fk_plain(conn, 'students',                'class_id', 'fk_students_class_cascade',           'students_class_id_fkey')