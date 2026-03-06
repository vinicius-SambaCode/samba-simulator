# app/routes/pdf.py
# -*- coding: utf-8 -*-
"""
Rotas de PDF (Sprint 2):
- Geração de caderno (ABNT) e cartão-resposta OMR
- Download por turma ou por aluno

Regras:
- Apenas COORDINATOR pode gerar PDFs do exame
- Exam precisa estar LOCKED (travado)

Paths de saída (padrão):
- storage/exams/{exam_id}/...
ou, com STORAGE_DIR=/app/storage:
- /app/storage/exams/{exam_id}/...
"""

from __future__ import annotations

import os
from typing import Optional, Literal
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user
from app.core.deps import require_role
from app.core.settings import settings  # <<< usado para resolver STORAGE_DIR

from app.models.base_models import User
from app.models.exam import Exam, ExamStatus
from app.models.school import SchoolClass, Student
from app.services.pdf_generator import (
    generate_exam_pdfs_for_class,
    generate_exam_pdfs_for_student,
    _exam_storage_dir,  # mantido para geração (compat)
)

router = APIRouter(prefix="/pdf", tags=["pdf"])


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def _get_exam_or_404(db: Session, exam_id: int) -> Exam:
    exam = db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Simulado não encontrado.")
    return exam


def _storage_root_abs() -> str:
    """
    Retorna o diretório raiz de storage como caminho ABSOLUTO.
    Preferência:
      1) settings.STORAGE_DIR (se definido)
      2) '/app/storage' (fallback)
    Se STORAGE_DIR vier relativo (ex.: 'storage'), ancoramos em '/app'.
    """
    raw = getattr(settings, "STORAGE_DIR", None) or "/app/storage"
    if os.path.isabs(raw):
        return raw
    # ancora no /app (WORKDIR do container)
    return os.path.join("/app", raw)


def _exam_dir_abs(exam_id: int) -> str:
    """
    Caminho ABSOLUTO do diretório do exame.
    (NÃO cria pasta; apenas retorna o caminho para verificação/uso em download.)
    """
    return os.path.join(_storage_root_abs(), "exams", str(exam_id))


# -------------------------------------------------------------------
# POST /pdf/exams/{exam_id}/pdf/generate  (por turma ou aluno)
# -------------------------------------------------------------------
@router.post(
    "/exams/{exam_id}/pdf/generate",
    dependencies=[Depends(require_role("COORDINATOR"))]
)
def generate_pdfs(
    exam_id: int,
    class_id: Optional[int] = None,
    student_id: Optional[int] = None,
    logo_path: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Gera PDFs:
    - Por turma: informar class_id
    - Por aluno: informar student_id
    - logo_path: opcional (caminho local no servidor)
    """
    exam = _get_exam_or_404(db, exam_id)
    if exam.status != ExamStatus.LOCKED:
        raise HTTPException(status_code=400, detail="Exame precisa estar LOCKED para gerar PDFs.")

    if class_id is None and student_id is None:
        raise HTTPException(status_code=400, detail="Informe class_id (turma) OU student_id (aluno).")

    if class_id is not None and student_id is not None:
        raise HTTPException(status_code=400, detail="Escolha apenas um: class_id OU student_id.")

    if class_id is not None:
        cls = db.get(SchoolClass, class_id)
        if not cls:
            raise HTTPException(status_code=400, detail="Turma inválida (class_id).")
        # Mantemos compat com serviços existentes
        result = generate_exam_pdfs_for_class(db, exam, class_id, logo_path=logo_path)
        return {"detail": "PDFs gerados para a turma.", "result": result}
    else:
        st = db.get(Student, student_id)
        if not st:
            raise HTTPException(status_code=400, detail="Aluno inválido (student_id).")
        result = generate_exam_pdfs_for_student(db, exam, student_id, logo_path=logo_path)
        return {"detail": "PDFs gerados para o aluno.", "result": result}


# -------------------------------------------------------------------
# GET /pdf/exams/{exam_id}/pdf/download?student_id=..&type=..
# -------------------------------------------------------------------
@router.get("/exams/{exam_id}/pdf/download")
def download_pdf(
    exam_id: int,
    type: Literal["booklet", "answer_sheet"] = "booklet",
    class_id: Optional[int] = None,     # reservado p/ futuro (zip por turma)
    student_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Download:
    - Por aluno: informar student_id e type = booklet|answer_sheet
    - Por turma: (modo simples) retorna um ZIP no futuro; por enquanto,
      gere e baixe individualmente (ou use os paths retornados).
    """
    _ = _get_exam_or_404(db, exam_id)

    if student_id is None:
        raise HTTPException(status_code=400, detail="Informe student_id para download unitário.")

    # >>> AJUSTE CRÍTICO: NÃO criar diretório no download
    # (Antes, _exam_storage_dir(...) criava pasta e estourava em alguns ambientes)
    base_dir = _exam_dir_abs(exam_id)

    if type == "booklet":
        filename = f"booklet_exam{exam_id}_student{student_id}.pdf"
    else:
        filename = f"omr_exam{exam_id}_student{student_id}_V1.pdf"

    file_path = os.path.join(base_dir, filename)

    if not os.path.exists(file_path):
        # Mantemos a mensagem original (orienta gerar antes de baixar)
        raise HTTPException(status_code=404, detail="Arquivo não encontrado. Gere o PDF antes de baixar.")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/pdf",
    )
