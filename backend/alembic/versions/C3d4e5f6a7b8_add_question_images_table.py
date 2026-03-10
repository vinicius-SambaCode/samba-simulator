"""add_question_images_table

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-07

Tabela question_images para imagens embutidas extraídas de .docx.
Usa IF NOT EXISTS — seguro de rodar mesmo se a tabela já foi criada manualmente.
"""

from alembic import op

revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS question_images (
            id           SERIAL PRIMARY KEY,
            question_id  INTEGER NOT NULL
                         REFERENCES questions(id) ON DELETE CASCADE,
            storage_path VARCHAR(512) NOT NULL,
            mime_type    VARCHAR(64)  NOT NULL DEFAULT 'image/png',
            context      VARCHAR(16)  NOT NULL DEFAULT 'stem',
            order_idx    INTEGER      NOT NULL DEFAULT 0,
            width_px     INTEGER,
            height_px    INTEGER,
            created_at   TIMESTAMP    NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_question_images_question_id
        ON question_images (question_id)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_question_images_question_id")
    op.execute("DROP TABLE IF EXISTS question_images")
