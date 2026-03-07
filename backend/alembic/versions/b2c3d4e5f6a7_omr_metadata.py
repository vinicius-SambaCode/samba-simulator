"""omr metadata fields on exams

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-06 00:00:00.000000

DESCRIÇÃO:
    Adiciona campos de metadados OMR (Optical Mark Recognition) à tabela
    `exams`. Esses campos controlam a geração da folha de respostas
    digitalizada que será usada na correção automática dos simulados.

    Campos adicionados:
        omr_rows          -> INTEGER NOT NULL DEFAULT 10
                             Número de linhas da grade de respostas.
                             Corresponde ao número máximo de questões
                             que cabem na folha. Padrão: 10.

        omr_cols          -> INTEGER NOT NULL DEFAULT 5
                             Número de colunas da grade (= alternativas).
                             Padrão: 5 (A, B, C, D, E).
                             Use 4 para simulados com apenas A-D.

        omr_header_fields -> TEXT NULL
                             JSON com os campos extras do cabeçalho.
                             Exemplo: '["nome", "turma", "numero"]'
                             O gerador de PDF (Passo 7) lê este campo
                             para renderizar o cabeçalho personalizado.
                             NULL = usa cabeçalho padrão da escola.

        barcode_enabled   -> BOOLEAN NOT NULL DEFAULT false
                             Se true, a folha terá QR-code ou código de
                             barras para identificação automática durante
                             a digitalização em lote.

DEPENDÊNCIAS:
    Revisa: a1b2c3d4e5f6 (teacher_progress e progress_log)
    Tabela alvo: exams (criada em 423e3074d76d)
"""

from __future__ import annotations
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# =============================================================================
# Identificadores da migration
# =============================================================================

revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# =============================================================================
# UPGRADE — adiciona as 4 colunas OMR na tabela exams
# =============================================================================

def upgrade() -> None:
    # -------------------------------------------------------------------------
    # omr_rows: número de linhas da grade de respostas
    # server_default="10" garante que simulados existentes não quebrem
    # -------------------------------------------------------------------------
    op.add_column(
        "exams",
        sa.Column(
            "omr_rows",
            sa.Integer(),
            nullable=False,
            server_default="10",
            comment="Número de linhas da grade OMR (= máximo de questões na folha)",
        ),
    )

    # -------------------------------------------------------------------------
    # omr_cols: número de colunas (= alternativas por questão)
    # server_default="5" → A, B, C, D, E
    # -------------------------------------------------------------------------
    op.add_column(
        "exams",
        sa.Column(
            "omr_cols",
            sa.Integer(),
            nullable=False,
            server_default="5",
            comment="Número de colunas da grade OMR (= número de alternativas)",
        ),
    )

    # -------------------------------------------------------------------------
    # omr_header_fields: campos do cabeçalho em JSON
    # Nullable: NULL significa "usar cabeçalho padrão"
    # -------------------------------------------------------------------------
    op.add_column(
        "exams",
        sa.Column(
            "omr_header_fields",
            sa.Text(),
            nullable=True,
            comment='JSON com campos do cabeçalho. Ex: \'["nome","turma","data"]\'',
        ),
    )

    # -------------------------------------------------------------------------
    # barcode_enabled: habilita QR-code/barcode na folha de respostas
    # server_default="false" → desabilitado por padrão
    # -------------------------------------------------------------------------
    op.add_column(
        "exams",
        sa.Column(
            "barcode_enabled",
            sa.Boolean(),
            nullable=False,
            server_default="false",
            comment="Se true, imprime QR-code/barcode na folha de respostas",
        ),
    )


# =============================================================================
# DOWNGRADE — remove as 4 colunas OMR
# =============================================================================

def downgrade() -> None:
    # Remove na ordem inversa da adição (boa prática, evita dependências)
    op.drop_column("exams", "barcode_enabled")
    op.drop_column("exams", "omr_header_fields")
    op.drop_column("exams", "omr_cols")
    op.drop_column("exams", "omr_rows")
