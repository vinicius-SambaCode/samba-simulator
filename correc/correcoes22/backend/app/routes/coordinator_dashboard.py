# -*- coding: utf-8 -*-
"""
app/routes/coordinator_dashboard.py
=====================================
Painel do coordenador: visão consolidada de progresso do simulado.

ENDPOINTS
---------
GET /exams/{exam_id}/dashboard
    Retorna o progresso cruzando turma × disciplina × professor.
    Fonte: ExamTeacherProgress (mantida atualizada pelo progress_service).

GET /exams/{exam_id}/dashboard/by-teacher
    Mesma informação agrupada por professor — útil para cobranças.

GET /exams/{exam_id}/dashboard/log
    Histórico de eventos de progresso (ExamProgressLog), paginado.
    Permite filtrar por teacher_user_id, discipline_id ou class_id.

LÓGICA DE AGRUPAMENTO (dashboard principal)
--------------------------------------------
O painel agrupa a saída em:

  turmas []
    └─ disciplines []
         └─ teachers []
              └─ { teacher_id, teacher_name, submitted, quota, status }

Se ExamTeacherProgress ainda não tiver registros para um recorte
(professor nunca inseriu questão), o endpoint consulta diretamente
ExamTeacherAssignment e preenche com submitted=0, status=PENDING.
Assim o coordenador vê TODOS os slots desde o momento do assign, sem
esperar a primeira questão.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import require_role
from app.models.exam import (
    Exam,
    ExamTeacherAssignment,
    ExamTeacherProgress,
    ExamProgressLog,
    ExamDisciplineQuota,
    ProgressStatus,
)
from app.models.school import SchoolClass
from app.models.models import Discipline
from app.models.base_models import User

router = APIRouter(prefix="/exams", tags=["coordinator-dashboard"])


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _get_exam_or_404(db: Session, exam_id: int) -> Exam:
    exam = db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Simulado não encontrado.")
    return exam


# ---------------------------------------------------------------------------
# GET /exams/{exam_id}/dashboard
# ---------------------------------------------------------------------------

@router.get(
    "/{exam_id}/dashboard",
    dependencies=[Depends(require_role("COORDINATOR"))],
    summary="Painel de progresso por turma × disciplina × professor",
)
def coordinator_dashboard(exam_id: int, db: Session = Depends(get_db)):
    exam = _get_exam_or_404(db, exam_id)

    # --- cotas por disciplina ------------------------------------------------
    quotas: dict[int, int] = {
        q.discipline_id: q.quota for q in exam.discipline_quotas
    }

    # --- progresso já registrado (pode estar incompleto se professor nunca
    #     inseriu questão) -----------------------------------------------------
    progress_index: dict[tuple, ExamTeacherProgress] = {
        (p.class_id, p.discipline_id, p.teacher_user_id): p
        for p in exam.teacher_progress
    }

    # --- monta visão a partir de ExamTeacherAssignment (fonte completa) ------
    # Agrupa: class_id → discipline_id → [teacher_slots]
    tree: dict[int, dict[int, list]] = {}

    for assign in exam.teacher_assignments:
        cid  = assign.class_id
        did  = assign.discipline_id
        tid  = assign.teacher_user_id

        if cid not in tree:
            tree[cid] = {}
        if did not in tree[cid]:
            tree[cid][did] = []

        quota = quotas.get(did, 0)
        # Conta questões reais do professor para esta disciplina (qualquer turma)
        submitted = (
            db.query(Question)
            .filter_by(exam_id=exam.id, discipline_id=did, author_user_id=tid)
            .filter(Question.state.in_(("SUBMITTED", "APPROVED", "submitted", "approved")))
            .count()
        )
        if submitted >= quota and quota > 0:
            status = ProgressStatus.COMPLETE.value
        elif submitted > 0:
            status = ProgressStatus.PARTIAL.value
        else:
            status = ProgressStatus.PENDING.value

        teacher_name = assign.teacher.name if hasattr(assign.teacher, "name") else str(tid)

        tree[cid][did].append({
            "teacher_user_id": tid,
            "teacher_name":    teacher_name,
            "submitted":       submitted,
            "quota":           quota,
            "remaining":       max(0, quota - submitted),
            "status":          status,
        })

    # --- converte para lista serializable ------------------------------------
    classes_out = []
    for cid, disc_map in tree.items():
        sc = db.get(SchoolClass, cid)
        class_name = sc.name if sc and hasattr(sc, "name") else str(cid)

        disciplines_out = []
        for did, teacher_slots in disc_map.items():
            disc = db.get(Discipline, did)
            disc_name = disc.name if disc and hasattr(disc, "name") else str(did)

            quota = quotas.get(did, 0)
            total_submitted = sum(s["submitted"] for s in teacher_slots)

            # status agregado da disciplina nesta turma
            if total_submitted >= quota and quota > 0:
                agg_status = ProgressStatus.COMPLETE.value
            elif total_submitted > 0:
                agg_status = ProgressStatus.PARTIAL.value
            else:
                agg_status = ProgressStatus.PENDING.value

            disciplines_out.append({
                "discipline_id":   did,
                "discipline_name": disc_name,
                "quota":           quota,
                "total_submitted": total_submitted,
                "remaining":       max(0, quota - total_submitted),
                "status":          agg_status,
                "teachers":        teacher_slots,
            })

        classes_out.append({
            "class_id":    cid,
            "class_name":  class_name,
            "disciplines": disciplines_out,
        })

    # --- resumo global do simulado -------------------------------------------
    # quota é por disciplina (não multiplica por turma)
    # submitted conta questões reais no banco (não por turma)
    total_quota     = sum(quotas.values())
    total_submitted = (
        db.query(Question)
        .filter(
            Question.exam_id == exam.id,
            Question.state.in_(("SUBMITTED", "APPROVED", "submitted", "approved")),
        )
        .count()
    )

    return {
        "exam_id":         exam.id,
        "exam_title":      exam.title,
        "exam_status":     exam.status,
        "total_quota":     total_quota,
        "total_submitted": total_submitted,
        "total_remaining": max(0, total_quota - total_submitted),
        "classes":         classes_out,
    }


# ---------------------------------------------------------------------------
# GET /exams/{exam_id}/dashboard/by-teacher
# ---------------------------------------------------------------------------

@router.get(
    "/{exam_id}/dashboard/by-teacher",
    dependencies=[Depends(require_role("COORDINATOR"))],
    summary="Progresso agrupado por professor",
)
def dashboard_by_teacher(exam_id: int, db: Session = Depends(get_db)):
    exam = _get_exam_or_404(db, exam_id)

    quotas: dict[int, int] = {
        q.discipline_id: q.quota for q in exam.discipline_quotas
    }

    progress_index: dict[tuple, ExamTeacherProgress] = {
        (p.class_id, p.discipline_id, p.teacher_user_id): p
        for p in exam.teacher_progress
    }

    # agrupa por teacher_user_id
    by_teacher: dict[int, dict] = {}

    for assign in exam.teacher_assignments:
        cid = assign.class_id
        did = assign.discipline_id
        tid = assign.teacher_user_id

        if tid not in by_teacher:
            teacher_name = assign.teacher.name if hasattr(assign.teacher, "name") else str(tid)
            by_teacher[tid] = {
                "teacher_user_id": tid,
                "teacher_name":    teacher_name,
                "slots":           [],
                "total_submitted": 0,
                "total_quota":     0,
            }

        prog  = progress_index.get((cid, did, tid))
        quota = quotas.get(did, 0)

        sc   = db.get(SchoolClass, cid)
        disc = db.get(Discipline, did)

        submitted = prog.submitted if prog else 0
        status    = prog.status    if prog else ProgressStatus.PENDING.value

        by_teacher[tid]["slots"].append({
            "class_id":        cid,
            "class_name":      sc.name if sc and hasattr(sc, "name") else str(cid),
            "discipline_id":   did,
            "discipline_name": disc.name if disc and hasattr(disc, "name") else str(did),
            "submitted":       submitted,
            "quota":           quota,
            "remaining":       max(0, quota - submitted),
            "status":          status,
        })
        by_teacher[tid]["total_submitted"] += submitted
        by_teacher[tid]["total_quota"]     += quota

    teachers_out = list(by_teacher.values())
    for t in teachers_out:
        t["overall_status"] = (
            ProgressStatus.COMPLETE.value if t["total_submitted"] >= t["total_quota"] and t["total_quota"] > 0
            else ProgressStatus.PARTIAL.value  if t["total_submitted"] > 0
            else ProgressStatus.PENDING.value
        )

    return {
        "exam_id":  exam.id,
        "teachers": teachers_out,
    }


# ---------------------------------------------------------------------------
# GET /exams/{exam_id}/dashboard/log
# ---------------------------------------------------------------------------

@router.get(
    "/{exam_id}/dashboard/log",
    dependencies=[Depends(require_role("COORDINATOR"))],
    summary="Histórico de eventos de progresso (paginado)",
)
def dashboard_log(
    exam_id: int,
    db: Session = Depends(get_db),
    teacher_user_id: Optional[int] = Query(None, description="Filtrar por professor"),
    discipline_id:   Optional[int] = Query(None, description="Filtrar por disciplina"),
    class_id:        Optional[int] = Query(None, description="Filtrar por turma"),
    limit:  int = Query(50,  ge=1, le=200),
    offset: int = Query(0,   ge=0),
):
    exam = _get_exam_or_404(db, exam_id)

    q = db.query(ExamProgressLog).filter(ExamProgressLog.exam_id == exam_id)

    if teacher_user_id:
        q = q.filter(ExamProgressLog.teacher_user_id == teacher_user_id)
    if discipline_id:
        q = q.filter(ExamProgressLog.discipline_id == discipline_id)
    if class_id:
        q = q.filter(ExamProgressLog.class_id == class_id)

    total  = q.count()
    events = q.order_by(ExamProgressLog.occurred_at.desc()).offset(offset).limit(limit).all()

    return {
        "exam_id": exam_id,
        "total":   total,
        "offset":  offset,
        "limit":   limit,
        "events": [
            {
                "id":              e.id,
                "event_type":      e.event_type,
                "teacher_user_id": e.teacher_user_id,
                "discipline_id":   e.discipline_id,
                "class_id":        e.class_id,
                "question_id":     e.question_id,
                "quota_before":    e.quota_before,
                "quota_after":     e.quota_after,
                "submitted_snap":  e.submitted_snap,
                "occurred_at":     e.occurred_at.isoformat() if e.occurred_at else None,
            }
            for e in events
        ],
    }
