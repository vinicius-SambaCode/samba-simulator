# -*- coding: utf-8 -*-
"""
app/routes/results.py
======================
Resultados dos simulados — lógica extraída do test_integration.py.

ENDPOINTS
---------
GET /exams/{exam_id}/results
    Com ?class_id=  → ranking da turma
    Com ?student_id= → resultado individual por disciplina

GET /exams/{exam_id}/results/summary
    Resumo global (todas as turmas com respostas)
"""

from __future__ import annotations
from typing import Optional
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import require_role
from app.models.exam import Exam, ExamQuestionLink
from app.models.school import SchoolClass, Student
from app.models.student_answer import StudentAnswer
from app.models.models import Discipline

router = APIRouter(prefix="/exams", tags=["results"])


def _get_exam_or_404(db: Session, exam_id: int) -> Exam:
    exam = db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Simulado não encontrado.")
    return exam


def _calc_nota(acertos: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round((acertos / total) * 10, 2)


# ---------------------------------------------------------------------------
# GET /exams/{exam_id}/results
# ---------------------------------------------------------------------------

@router.get(
    "/{exam_id}/results",
    dependencies=[Depends(require_role("COORDINATOR", "ADMIN", "TEACHER"))],
    summary="Resultados por turma (ranking) ou individual por aluno",
)
def get_results(
    exam_id:    int,
    db:         Session = Depends(get_db),
    class_id:   Optional[int] = Query(None),
    student_id: Optional[int] = Query(None),
):
    exam = _get_exam_or_404(db, exam_id)

    links = (
        db.query(ExamQuestionLink)
        .filter(ExamQuestionLink.exam_id == exam_id)
        .order_by(ExamQuestionLink.order_idx)
        .all()
    )
    if not links:
        raise HTTPException(status_code=404, detail="Nenhuma questão vinculada ao simulado.")

    total_questoes = len(links)
    link_ids       = {l.id for l in links}

    link_disc:  dict[int, int] = {}
    disc_names: dict[int, str] = {}
    for l in links:
        did = l.question.discipline_id
        link_disc[l.id] = did
        if did not in disc_names:
            disc = db.get(Discipline, did)
            disc_names[did] = disc.name if disc else f"Disc. #{did}"

    # -----------------------------------------------------------------------
    # RESULTADO INDIVIDUAL
    # -----------------------------------------------------------------------
    if student_id is not None:
        student = db.get(Student, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Aluno não encontrado.")

        answers = (
            db.query(StudentAnswer)
            .filter(
                StudentAnswer.exam_id    == exam_id,
                StudentAnswer.student_id == student_id,
            )
            .all()
        )

        answered      = {a.question_link_id: a for a in answers}
        acertos_total = sum(1 for a in answers if a.is_correct)

        by_disc: dict[int, dict] = defaultdict(lambda: {"acertos": 0, "total": 0})
        for lid in link_ids:
            did = link_disc[lid]
            by_disc[did]["total"] += 1
            if lid in answered and answered[lid].is_correct:
                by_disc[did]["acertos"] += 1

        por_disciplina = [
            {
                "discipline_id":   did,
                "discipline_name": disc_names.get(did, f"Disc. #{did}"),
                "acertos":         v["acertos"],
                "total":           v["total"],
                "nota":            _calc_nota(v["acertos"], v["total"]),
            }
            for did, v in sorted(by_disc.items())
        ]

        return {
            "exam_id":        exam_id,
            "exam_title":     exam.title,
            "student_id":     student_id,
            "student_name":   student.name,
            "student_ra":     student.ra,
            "acertos":        acertos_total,
            "total":          total_questoes,
            "nota":           _calc_nota(acertos_total, total_questoes),
            "por_disciplina": por_disciplina,
        }

    # -----------------------------------------------------------------------
    # RANKING DA TURMA
    # -----------------------------------------------------------------------
    if class_id is not None:
        sc = db.get(SchoolClass, class_id)
        if not sc:
            raise HTTPException(status_code=404, detail="Turma não encontrada.")

        students = (
            db.query(Student)
            .filter(Student.class_id == class_id)
            .order_by(Student.name)
            .all()
        )
        if not students:
            return {
                "exam_id":        exam_id,
                "exam_title":     exam.title,
                "class_id":       class_id,
                "class_name":     sc.name,
                "total_students": 0,
                "media_turma":    0,
                "aprovados":      0,
                "reprovados":     0,
                "results":        [],
            }

        student_ids = [s.id for s in students]

        all_answers = (
            db.query(StudentAnswer)
            .filter(
                StudentAnswer.exam_id    == exam_id,
                StudentAnswer.student_id.in_(student_ids),
            )
            .all()
        )

        by_student: dict[int, list] = defaultdict(list)
        for a in all_answers:
            by_student[a.student_id].append(a)

        rows = []
        for s in students:
            ans     = by_student.get(s.id, [])
            acertos = sum(1 for a in ans if a.is_correct)
            rows.append({
                "student_id":   s.id,
                "student_name": s.name,
                "student_ra":   s.ra,
                "acertos":      acertos,
                "total":        total_questoes,
                "nota":         _calc_nota(acertos, total_questoes),
                "respondidas":  len(ans),
            })

        rows.sort(key=lambda r: (-r["nota"], r["student_name"]))
        for i, r in enumerate(rows, 1):
            r["ranking"] = i

        notas     = [r["nota"] for r in rows]
        media     = round(sum(notas) / len(notas), 2) if notas else 0
        aprovados = sum(1 for n in notas if n >= 5)

        return {
            "exam_id":        exam_id,
            "exam_title":     exam.title,
            "class_id":       class_id,
            "class_name":     sc.name,
            "total_students": len(rows),
            "media_turma":    media,
            "aprovados":      aprovados,
            "reprovados":     len(rows) - aprovados,
            "results":        rows,
        }

    raise HTTPException(
        status_code=400,
        detail="Informe class_id para ranking ou student_id para resultado individual.",
    )


# ---------------------------------------------------------------------------
# GET /exams/{exam_id}/results/summary
# ---------------------------------------------------------------------------

@router.get(
    "/{exam_id}/results/summary",
    dependencies=[Depends(require_role("COORDINATOR", "ADMIN", "TEACHER"))],
    summary="Resumo global do simulado por turma",
)
def get_results_summary(exam_id: int, db: Session = Depends(get_db)):
    exam           = _get_exam_or_404(db, exam_id)
    links          = db.query(ExamQuestionLink).filter(ExamQuestionLink.exam_id == exam_id).all()
    total_questoes = len(links)

    if not total_questoes:
        return {"exam_id": exam_id, "exam_title": exam.title, "total_questoes": 0, "classes": []}

    rows = db.execute(text("""
        SELECT sc.id, sc.name,
               COUNT(DISTINCT sa.student_id)                  AS n_students,
               SUM(CASE WHEN sa.is_correct THEN 1 ELSE 0 END) AS acertos,
               COUNT(sa.id)                                    AS respondidas
        FROM student_answers sa
        JOIN students       st ON st.id = sa.student_id
        JOIN school_classes sc ON sc.id = st.class_id
        WHERE sa.exam_id = :eid
        GROUP BY sc.id, sc.name
        ORDER BY sc.name
    """), {"eid": exam_id}).fetchall()

    classes_out = []
    for row in rows:
        n_st    = row[2]
        acertos = row[3] or 0
        total   = n_st * total_questoes if n_st else 0
        media   = round((acertos / total) * 10, 2) if total else 0
        classes_out.append({
            "class_id":        row[0],
            "class_name":      row[1],
            "total_students":  n_st,
            "media_turma":     media,
            "acertos":         acertos,
            "total_respostas": row[4],
        })

    return {
        "exam_id":        exam_id,
        "exam_title":     exam.title,
        "exam_status":    exam.status,
        "total_questoes": total_questoes,
        "classes":        classes_out,
    }

# ---------------------------------------------------------------------------
# GET /exams/{exam_id}/results/questions
# ---------------------------------------------------------------------------

@router.get(
    "/{exam_id}/results/questions",
    dependencies=[Depends(require_role("COORDINATOR", "ADMIN", "TEACHER"))],
    summary="Taxa de acerto por questão, com distribuição de marcação",
)
def get_question_stats(
    exam_id:  int,
    class_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    from app.models.exam import Question

    exam  = _get_exam_or_404(db, exam_id)
    links = (
        db.query(ExamQuestionLink)
        .filter(ExamQuestionLink.exam_id == exam_id)
        .order_by(ExamQuestionLink.order_idx)
        .all()
    )
    if not links:
        return {"exam_id": exam_id, "questions": []}

    link_ids = [l.id for l in links]

    # Filtra respostas por turma se informado
    sa_q = db.query(StudentAnswer).filter(StudentAnswer.question_link_id.in_(link_ids))
    if class_id:
        sa_q = sa_q.join(Student, Student.id == StudentAnswer.student_id).filter(Student.class_id == class_id)
    answers = sa_q.all()

    # Agrupa respostas por link_id
    by_link: dict[int, list] = defaultdict(list)
    for a in answers:
        by_link[a.question_link_id].append(a)

    result = []
    for i, link in enumerate(links):
        q = link.question
        ans_list = by_link[link.id]
        total_resp = len(ans_list)
        acertos    = sum(1 for a in ans_list if a.is_correct)

        # Distribuição de marcação por alternativa
        dist: dict[str, int] = {}
        for a in ans_list:
            if a.marked_label:
                dist[a.marked_label] = dist.get(a.marked_label, 0) + 1

        taxa = round(acertos / total_resp * 100, 1) if total_resp else None

        result.append({
            "order":         i + 1,
            "question_id":   q.id,
            "link_id":       link.id,
            "stem_preview":  (q.stem or "")[:120] + ("…" if len(q.stem or "") > 120 else ""),
            "correct_label": link.correct_label,
            "discipline_id": q.discipline_id,
            "total_respostas": total_resp,
            "acertos":       acertos,
            "taxa_acerto":   taxa,
            "distribuicao":  dist,
        })

    return {"exam_id": exam_id, "exam_title": exam.title, "questions": result}