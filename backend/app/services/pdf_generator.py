# app/services/pdf_generator.py
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Any, Optional, List

from app.core.settings import settings
# Se você já tem outros imports (ex.: reportlab, parsers etc.), mantenha-os aqui.


# ------------------------------------------------------------
# Diretórios de storage (robustos)
# ------------------------------------------------------------
def _coerce_storage_dir(raw: Optional[str]) -> Path:
    """
    Garante que STORAGE_DIR seja absoluto e existente.
    Preferência:
      1) settings.STORAGE_DIR
      2) '/app/storage' (fallback)
    """
    base = Path(raw or "/app/storage")
    if not base.is_absolute():
        # ancora no /app (WORKDIR do container)
        base = Path("/app") / base
    base.mkdir(parents=True, exist_ok=True)  # cria diretório raiz do storage
    return base


_STORAGE_ROOT = _coerce_storage_dir(getattr(settings, "STORAGE_DIR", None))


def exam_storage_dir(exam_id: int, create: bool = False) -> Path:
    """
    Retorna o diretório do exame:
      /app/storage/exams/{exam_id}
    - create=False: não cria nada (uso em download)
    - create=True : cria diretórios recursivamente (uso em geração)
    """
    base = _STORAGE_ROOT / "exams" / str(exam_id)
    if create:
        base.mkdir(parents=True, exist_ok=True)
    return base


# Mantém compatibilidade com código legado que chamava _exam_storage_dir
def _exam_storage_dir(exam_id: int) -> str:
    """Compat layer antigo: cria e retorna o caminho (str)."""
    p = exam_storage_dir(exam_id, create=True)
    return str(p)


# ------------------------------------------------------------
# EXEMPLOS de APIs de geração (mantenha as suas funções atuais)
# ------------------------------------------------------------
def generate_exam_pdfs_for_class(
    db, exam, class_id: int, logo_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Gera PDFs para a turma.
    (Implementação original do seu projeto permanece; esta função só garante paths.)
    """
    out_dir = exam_storage_dir(exam.id, create=True)
    # TODO: sua lógica de geração aqui (mantida)
    # Exemplo no retorno:
    return {"output_dir": str(out_dir), "class_id": class_id, "generated": True}


def generate_exam_pdfs_for_student(
    db, exam, student_id: int, logo_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Gera PDFs para um aluno específico.
    """
    out_dir = exam_storage_dir(exam.id, create=True)
    # TODO: sua lógica de geração aqui (mantida)
    return {"output_dir": str(out_dir), "student_id": student_id, "generated": True}
