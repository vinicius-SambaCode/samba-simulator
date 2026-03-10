# app/routes/omr.py
# -*- coding: utf-8 -*-
"""
Rotas do Passo 14:
  POST /exams/{exam_id}/omr/upload          → upload PDF escaneado, processa OMR
  GET  /exams/{exam_id}/results             → resultados da turma
  GET  /exams/{exam_id}/results/export      → XLSX por série
  GET  /exams/{exam_id}/results/report/{student_id} → PDF devolutiva individual
  PATCH /exams/{exam_id}/links/{link_id}/answer     → atualiza gabarito manualmente
"""

from __future__ import annotations

import io
from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse, Response
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user
from app.core.deps import require_role
from app.models.base_models import User
from app.models.exam import Exam, ExamStatus, ExamQuestionLink

router = APIRouter(tags=["omr"])


def _get_exam_or_404(db: Session, exam_id: int) -> Exam:
    exam = db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Simulado não encontrado.")
    return exam


# ---------------------------------------------------------------------------
# PATCH /exams/{exam_id}/links/{link_id}/answer  — gabarito manual
# ---------------------------------------------------------------------------
@router.patch(
    "/exams/{exam_id}/links/{link_id}/answer",
    dependencies=[Depends(require_role("COORDINATOR"))],
)
def update_correct_label(
    exam_id: int,
    link_id: int,
    answer: str,
    db: Session = Depends(get_db),
):
    """
    Atualiza o gabarito de uma questão manualmente.
    answer deve ser uma letra: A, B, C, D ou E.
    """
    answer = answer.strip().upper()
    if answer not in ("A", "B", "C", "D", "E"):
        raise HTTPException(status_code=400, detail="Resposta inválida. Use A, B, C, D ou E.")

    link = db.query(ExamQuestionLink).filter_by(id=link_id, exam_id=exam_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link de questão não encontrado.")

    link.correct_label = answer
    db.commit()
    return {"detail": f"Gabarito Q{link.order_idx+1} atualizado → {answer}"}


# ---------------------------------------------------------------------------
# GET /exams/{exam_id}/links  — consulta gabarito atual
# ---------------------------------------------------------------------------
@router.get("/exams/{exam_id}/links")
def get_exam_links(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retorna todos os links de questões com gabarito."""
    _get_exam_or_404(db, exam_id)
    links = (
        db.query(ExamQuestionLink)
        .filter(ExamQuestionLink.exam_id == exam_id)
        .order_by(ExamQuestionLink.order_idx)
        .all()
    )
    return [
        {
            "id":            l.id,
            "order_idx":     l.order_idx,
            "question_id":   l.question_id,
            "correct_label": l.correct_label,
        }
        for l in links
    ]


# ---------------------------------------------------------------------------
# POST /exams/{exam_id}/omr/upload  — processa PDF escaneado
# ---------------------------------------------------------------------------
@router.post(
    "/exams/{exam_id}/omr/upload",
    dependencies=[Depends(require_role("COORDINATOR"))],
)
async def upload_omr_scan(
    exam_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Faz upload de um PDF escaneado com folhas OMR preenchidas.
    Cada página deve conter um barcode SAMBA-E{exam_id}-S{student_id}.
    O sistema detecta as bolhas e salva as respostas automaticamente.
    """
    exam = _get_exam_or_404(db, exam_id)
    if exam.status != ExamStatus.LOCKED:
        raise HTTPException(status_code=400, detail="Exame precisa estar LOCKED.")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Envie um arquivo PDF.")

    pdf_bytes = await file.read()
    if len(pdf_bytes) > 50 * 1024 * 1024:  # 50 MB limite
        raise HTTPException(status_code=400, detail="Arquivo muito grande (máx 50 MB).")

    try:
        from app.services.omr_scanner import process_omr_pdf
        result = process_omr_pdf(pdf_bytes, db, expected_exam_id=exam_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento OMR: {e}")

    return {
        "detail":         "Processamento OMR concluído.",
        "pages_total":    result.get("pages", 0),
        "pages_ok":       result.get("processed", 0),
        "answers_saved":  result.get("answers_saved", 0),
        "errors":         result.get("errors", []),
    }


# ---------------------------------------------------------------------------
# GET /exams/{exam_id}/results  — resultados da turma
# ---------------------------------------------------------------------------
@router.get("/exams/{exam_id}/results")
def get_results(
    exam_id: int,
    class_id: Optional[int] = None,
    student_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retorna resultados:
    - class_id  → todos os alunos da turma com ranking
    - student_id → resultado individual detalhado
    """
    _get_exam_or_404(db, exam_id)

    if class_id is None and student_id is None:
        raise HTTPException(status_code=400, detail="Informe class_id ou student_id.")

    from app.services.results_service import get_class_results, get_student_result

    if class_id is not None:
        return get_class_results(db, exam_id, class_id)
    else:
        result = get_student_result(db, exam_id, student_id)
        if not result:
            raise HTTPException(status_code=404, detail="Resultado não encontrado.")
        return result


# ---------------------------------------------------------------------------
# GET /exams/{exam_id}/results/export  — XLSX por série
# ---------------------------------------------------------------------------
@router.get("/exams/{exam_id}/results/export")
def export_results(
    exam_id: int,
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Exporta planilha XLSX com resultados da turma."""
    from app.models.school import SchoolClass
    from app.services.results_service import export_results_xlsx

    _get_exam_or_404(db, exam_id)
    cls = db.get(SchoolClass, class_id)
    if not cls:
        raise HTTPException(status_code=400, detail="Turma inválida.")

    xlsx_bytes = export_results_xlsx(db, exam_id, class_id)
    class_name = (cls.name or str(class_id)).replace(" ", "").replace("/", "-")
    filename   = f"resultados_{class_name}_exam{exam_id}.xlsx"

    return Response(
        content     = xlsx_bytes,
        media_type  = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers     = {"Content-Disposition": f"attachment; filename={filename}"},
    )


# ---------------------------------------------------------------------------
# GET /exams/{exam_id}/results/report/{student_id}  — PDF devolutiva
# ---------------------------------------------------------------------------
@router.get("/exams/{exam_id}/results/report/{student_id}")
def export_student_report(
    exam_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Gera PDF devolutiva individual para o aluno."""
    from app.services.results_service import export_report_pdf

    _get_exam_or_404(db, exam_id)
    try:
        pdf_bytes = export_report_pdf(db, exam_id, student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return Response(
        content    = pdf_bytes,
        media_type = "application/pdf",
        headers    = {"Content-Disposition": f"attachment; filename=devolutiva_exam{exam_id}_student{student_id}.pdf"},
    )


# ---------------------------------------------------------------------------
# GET /exams/{exam_id}/results/export/reports  — ZIP devolutivas por turma
# ---------------------------------------------------------------------------
@router.get("/exams/{exam_id}/results/export/reports")
def export_class_reports(
    exam_id: int,
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Gera ZIP com PDF de devolutiva individual para cada aluno da turma."""
    from app.models.school import SchoolClass
    from app.services.results_service import export_class_reports_zip

    _get_exam_or_404(db, exam_id)
    cls = db.get(SchoolClass, class_id)
    if not cls:
        raise HTTPException(status_code=400, detail="Turma inválida.")

    zip_bytes  = export_class_reports_zip(db, exam_id, class_id)
    class_name = (cls.name or str(class_id)).replace(" ", "").replace("/", "-")
    filename   = f"devolutivas_{class_name}_exam{exam_id}.zip"

    return Response(
        content    = zip_bytes,
        media_type = "application/zip",
        headers    = {"Content-Disposition": f"attachment; filename={filename}"},
    )
