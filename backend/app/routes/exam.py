# -*- coding: utf-8 -*-
"""
Rotas do módulo de Simulados (Sprint 1 + Passo 9)

MUDANÇAS DO PASSO 9
-------------------
- create_question:   chama record_question_added() após db.flush() da questão
- paste_questions:   chama record_question_added() para cada questão criada
- set_quotas:        chama sync_quota_change() após cada upsert de cota
- ExamOut schema:    corrigido model_config para from_attributes=True
"""

from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.db import get_db
from app.core.deps import require_role
from app.core.security import get_current_user
from app.models.base_models import User
from app.models.models import Discipline
from app.models.school import SchoolClass

from app.models.exam import (
    Exam, ExamStatus, AnswerSource,
    ExamClassAssignment, ExamDisciplineQuota, ExamTeacherAssignment,
    TeacherClassSubject,
    Question, QuestionOption, ExamQuestionLink,
)
from app.schemas.exam import (
    ExamCreate, ExamOut, AssignClassesIn, SetQuotasIn, AssignTeachersIn,
    QuestionCreate, BulkPasteIn
)
from app.services.question_parser import parse_pasted_questions
from app.services.progress_service import (
    record_question_added,
    sync_quota_change,
)


router = APIRouter(prefix="/exams", tags=["exams"])


# ----------------------------
# Helpers de busca e validação
# ----------------------------
def _get_exam_or_404(db: Session, exam_id: int) -> Exam:
    exam = db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Simulado não encontrado.")
    return exam


def _assert_status(exam: Exam, allowed: List[ExamStatus]):
    if exam.status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Ação inválida no status atual do simulado ({exam.status})."
        )


def _validate_options_count(exam: Exam, options: List[Dict]):
    labels = {opt["label"].upper() for opt in options}
    needed = {"A", "B", "C", "D"} if exam.options_count == 4 else {"A", "B", "C", "D", "E"}
    if labels != needed:
        raise HTTPException(
            status_code=400,
            detail=f"Alternativas inválidas: esperado {sorted(needed)}, recebido {sorted(labels)}."
        )


def _teacher_can_feed(db: Session, exam: Exam, current_user: User, class_id: int, discipline_id: int):
    assign = db.query(ExamTeacherAssignment).filter_by(
        exam_id=exam.id,
        class_id=class_id,
        discipline_id=discipline_id,
        teacher_user_id=current_user.id
    ).first()
    if not assign:
        raise HTTPException(status_code=403, detail="Você não está atribuído a esta turma/disciplina no simulado.")


def _next_order_idx(db: Session, exam_id: int) -> int:
    max_order = db.query(func.max(ExamQuestionLink.order_idx)).filter(
        ExamQuestionLink.exam_id == exam_id
    ).scalar()
    return (max_order or 0) + 1


def _ensure_selection_link(
    db: Session,
    exam: Exam,
    question_id: int,
    correct_label: str | None,
    force_create_without_correct: bool = False,
):
    existing = db.query(ExamQuestionLink).filter_by(
        exam_id=exam.id, question_id=question_id
    ).first()
    if existing:
        if correct_label and existing.correct_label != correct_label:
            existing.correct_label = correct_label
            db.add(existing)
        return

    if correct_label or force_create_without_correct:
        order_idx = _next_order_idx(db, exam.id)
        db.add(ExamQuestionLink(
            exam_id=exam.id,
            question_id=question_id,
            order_idx=order_idx,
            correct_label=correct_label
        ))


# ----------------------------
# Criar simulado (Coordenador)
# ----------------------------
@router.post("/", response_model=ExamOut, dependencies=[Depends(require_role("COORDINATOR"))])
def create_exam(data: ExamCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if data.options_count not in (4, 5):
        raise HTTPException(status_code=400, detail="options_count deve ser 4 ou 5.")

    exam = Exam(
        title=data.title,
        area=data.area,
        options_count=data.options_count,
        answer_source=data.answer_source,
        status=ExamStatus.COLLECTING,
        created_by_user_id=current_user.id
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam


# ----------------------------
# Alocar turmas ao simulado (Coord)
# ----------------------------
@router.post("/{exam_id}/assign-classes", dependencies=[Depends(require_role("COORDINATOR"))])
def assign_classes(exam_id: int, payload: AssignClassesIn, db: Session = Depends(get_db)):
    exam = _get_exam_or_404(db, exam_id)
    _assert_status(exam, [ExamStatus.COLLECTING])

    classes = db.query(SchoolClass).filter(SchoolClass.id.in_(payload.class_ids)).all()
    if len(classes) != len(payload.class_ids):
        raise HTTPException(status_code=400, detail="Há turmas inválidas na lista.")

    existing = {x.class_id for x in exam.class_assignments}
    for cid in payload.class_ids:
        if cid not in existing:
            db.add(ExamClassAssignment(exam_id=exam.id, class_id=cid))

    db.commit()
    return {"detail": "Turmas atribuídas."}


# ----------------------------
# Definir cotas por disciplina (Coord)
# ← PASSO 9: chama sync_quota_change após cada upsert
# ----------------------------
@router.post("/{exam_id}/quotas", dependencies=[Depends(require_role("COORDINATOR"))])
def set_quotas(exam_id: int, payload: SetQuotasIn, db: Session = Depends(get_db)):
    exam = _get_exam_or_404(db, exam_id)
    _assert_status(exam, [ExamStatus.COLLECTING])

    disc_ids = [it.discipline_id for it in payload.items]
    discs = db.query(Discipline).filter(Discipline.id.in_(disc_ids)).all()
    if len(discs) != len(payload.items):
        raise HTTPException(status_code=400, detail="Há disciplinas inválidas.")

    existing = {q.discipline_id: q for q in exam.discipline_quotas}
    for it in payload.items:
        if it.quota <= 0:
            raise HTTPException(status_code=400, detail="Quota deve ser > 0.")
        if it.discipline_id in existing:
            existing[it.discipline_id].quota = it.quota
        else:
            db.add(ExamDisciplineQuota(exam_id=exam.id, discipline_id=it.discipline_id, quota=int(it.quota)))

        # ← NOVO: propaga mudança de cota para todos os progress existentes
        sync_quota_change(db, exam.id, it.discipline_id, it.quota)

    db.commit()
    return {"detail": "Cotas definidas."}


# ----------------------------
# Atribuir professores (Coord)
# ----------------------------
@router.post("/{exam_id}/assign-teachers", dependencies=[Depends(require_role("COORDINATOR"))])
def assign_teachers(exam_id: int, payload: AssignTeachersIn, db: Session = Depends(get_db)):
    exam = _get_exam_or_404(db, exam_id)
    _assert_status(exam, [ExamStatus.COLLECTING])

    for it in payload.items:
        exists = db.query(TeacherClassSubject).filter_by(
            class_id=it.class_id,
            discipline_id=it.discipline_id,
            teacher_user_id=it.teacher_user_id
        ).first()
        if not exists:
            raise HTTPException(
                status_code=400,
                detail=f"Professor {it.teacher_user_id} não ministra esta disciplina nesta turma."
            )

    existing = {(a.class_id, a.discipline_id, a.teacher_user_id): a for a in exam.teacher_assignments}
    for it in payload.items:
        key = (it.class_id, it.discipline_id, it.teacher_user_id)
        if key not in existing:
            db.add(ExamTeacherAssignment(
                exam_id=exam.id,
                class_id=it.class_id,
                discipline_id=it.discipline_id,
                teacher_user_id=it.teacher_user_id
            ))

    db.commit()
    return {"detail": "Professores atribuídos ao simulado."}


# ----------------------------
# Alimentação de questões (Teacher)
# ← PASSO 9: chama record_question_added após cada questão
# ----------------------------
@router.post("/{exam_id}/questions", dependencies=[Depends(require_role("TEACHER"))])
def create_question(
    exam_id: int,
    payload: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exam = _get_exam_or_404(db, exam_id)
    _assert_status(exam, [ExamStatus.COLLECTING])
    _teacher_can_feed(db, exam, current_user, payload.class_id, payload.discipline_id)

    opts = [{"label": o.label.strip().upper(), "text": o.text.strip()} for o in payload.options]
    _validate_options_count(exam, opts)

    q = Question(
        exam_id=exam.id,
        discipline_id=payload.discipline_id,
        class_id=payload.class_id,
        author_user_id=current_user.id,
        source="manual",
        state="submitted",
        stem=payload.stem,
        has_images=False,
    )
    db.add(q)
    db.flush()  # obter q.id

    for o in opts:
        db.add(QuestionOption(question_id=q.id, label=o["label"], text=o["text"]))

    if exam.answer_source == AnswerSource.TEACHERS and payload.correct_label:
        corr = payload.correct_label.strip().upper()
        labels = {o["label"] for o in opts}
        if corr not in labels:
            raise HTTPException(status_code=400, detail="correct_label não está entre as alternativas da questão.")
        _ensure_selection_link(db, exam, q.id, corr)

    # ← NOVO: atualiza ExamTeacherProgress + log
    record_question_added(db, exam, q)

    db.commit()
    return {"detail": "Questão registrada."}


@router.post("/{exam_id}/questions/paste", dependencies=[Depends(require_role("TEACHER"))])
def paste_questions(
    exam_id: int,
    payload: BulkPasteIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exam = _get_exam_or_404(db, exam_id)
    _assert_status(exam, [ExamStatus.COLLECTING])
    _teacher_can_feed(db, exam, current_user, payload.class_id, payload.discipline_id)

    parsed = parse_pasted_questions(payload.content)
    created = 0
    for item in parsed:
        opts = [{"label": o["label"].strip().upper(), "text": o["text"].strip()} for o in item["options"]]
        _validate_options_count(exam, opts)

        q = Question(
            exam_id=exam.id,
            discipline_id=payload.discipline_id,
            class_id=payload.class_id,
            author_user_id=current_user.id,
            source="paste",
            state="submitted",
            stem=item["stem"],
            has_images=False,
        )
        db.add(q)
        db.flush()

        for o in opts:
            db.add(QuestionOption(question_id=q.id, label=o["label"], text=o["text"]))

        if exam.answer_source == AnswerSource.TEACHERS:
            corr = item.get("correct_label")
            if corr:
                corr = corr.strip().upper()
                if corr in {o["label"] for o in opts}:
                    _ensure_selection_link(db, exam, q.id, corr)

        # ← NOVO: atualiza ExamTeacherProgress + log para cada questão
        record_question_added(db, exam, q)
        created += 1

    db.commit()
    return {"detail": f"{created} questão(ões) incluída(s)."}


# ----------------------------
# Progresso (Coord/Teacher) — contadores por cota
# Mantido para compatibilidade; use /dashboard para visão completa
# ----------------------------
@router.get("/{exam_id}/progress")
def exam_progress(exam_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    exam = _get_exam_or_404(db, exam_id)

    quotas = {q.discipline_id: q.quota for q in exam.discipline_quotas}

    q_counts = (
        db.query(Question.discipline_id)
          .filter(Question.exam_id == exam.id, Question.state.in_(("submitted", "approved")))
          .all()
    )
    agg: Dict[int, int] = {}
    for (disc_id,) in q_counts:
        agg[disc_id] = agg.get(disc_id, 0) + 1

    items = []
    for disc_id, quota in quotas.items():
        items.append({
            "discipline_id": disc_id,
            "quota": quota,
            "submitted": agg.get(disc_id, 0),
            "remaining": max(0, quota - agg.get(disc_id, 0)),
        })

    return {
        "exam_id": exam.id,
        "status": exam.status,
        "options_count": exam.options_count,
        "answer_source": exam.answer_source,
        "disciplines": items,
    }


# ----------------------------
# Fechar coleta / revisão / travar
# ----------------------------
@router.post("/{exam_id}/lock", dependencies=[Depends(require_role("COORDINATOR"))])
def lock_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = _get_exam_or_404(db, exam_id)
    _assert_status(exam, [ExamStatus.COLLECTING, ExamStatus.REVIEW])

    quotas = {q.discipline_id: q.quota for q in exam.discipline_quotas}
    counts = {d: 0 for d in quotas}
    for q in exam.questions:
        if q.state in ("submitted", "approved"):
            counts[q.discipline_id] = counts.get(q.discipline_id, 0) + 1

    missing = {d for d, quota in quotas.items() if counts.get(d, 0) < quota}
    if missing:
        raise HTTPException(status_code=400, detail=f"Faltam questões para as disciplinas: {sorted(list(missing))}")

    for q in exam.questions:
        labels = {o.label.upper() for o in q.options}
        if exam.options_count == 4 and labels != {"A", "B", "C", "D"}:
            raise HTTPException(status_code=400, detail=f"Questão {q.id} não tem alternativas A-D corretas.")
        if exam.options_count == 5 and labels != {"A", "B", "C", "D", "E"}:
            raise HTTPException(status_code=400, detail=f"Questão {q.id} não tem alternativas A-E corretas.")

    if exam.answer_source == AnswerSource.TEACHERS:
        if not exam.selection:
            for q in sorted(exam.questions, key=lambda x: x.id):
                raise HTTPException(status_code=400, detail=f"Questão {q.id} sem gabarito (correct_label).")

    exam.status = ExamStatus.LOCKED
    db.add(exam)
    db.commit()
    return {"detail": "Simulado travado para geração."}
