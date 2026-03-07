# -*- coding: utf-8 -*-
"""
app/services/progress_service.py
=================================
Mantém ExamTeacherProgress e ExamProgressLog sincronizados após cada
inserção/remoção de questão, e após mudanças de cota.

USO NAS ROTAS
-------------
    from app.services.progress_service import record_question_added

    # dentro de create_question / paste_questions, APÓS db.flush() da questão:
    record_question_added(db, exam, question)
    # commit() continua sendo feito pela rota (sem mudança)

    # dentro de set_quotas, APÓS atualizar ExamDisciplineQuota:
    sync_quota_change(db, exam.id, discipline_id, new_quota)
    # commit() feito pela rota
"""

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.exam import (
    Exam,
    ExamDisciplineQuota,
    ExamTeacherProgress,
    ExamProgressLog,
    ProgressStatus,
    ProgressLogEvent,
)


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _get_quota(db: Session, exam_id: int, discipline_id: int) -> int:
    row = db.query(ExamDisciplineQuota).filter_by(
        exam_id=exam_id, discipline_id=discipline_id
    ).first()
    return row.quota if row else 0


def _get_or_create_progress(
    db: Session,
    exam_id: int,
    teacher_user_id: int,
    discipline_id: int,
    class_id: int,
    quota: int,
) -> ExamTeacherProgress:
    prog = db.query(ExamTeacherProgress).filter_by(
        exam_id=exam_id,
        teacher_user_id=teacher_user_id,
        discipline_id=discipline_id,
        class_id=class_id,
    ).first()

    if prog is None:
        prog = ExamTeacherProgress(
            exam_id=exam_id,
            teacher_user_id=teacher_user_id,
            discipline_id=discipline_id,
            class_id=class_id,
            quota=quota,
            submitted=0,
            status=ProgressStatus.PENDING.value,
            last_updated_at=datetime.utcnow(),
        )
        db.add(prog)
        db.flush()  # garante prog.id antes do log

    return prog


def _append_log(
    db: Session,
    prog: ExamTeacherProgress,
    event_type: ProgressLogEvent,
    question_id: int | None = None,
    quota_before: int | None = None,
    quota_after: int | None = None,
) -> None:
    db.add(ExamProgressLog(
        exam_id=prog.exam_id,
        teacher_user_id=prog.teacher_user_id,
        discipline_id=prog.discipline_id,
        class_id=prog.class_id,
        event_type=event_type.value,
        question_id=question_id,
        quota_before=quota_before,
        quota_after=quota_after,
        submitted_snap=prog.submitted,
        occurred_at=datetime.utcnow(),
    ))


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def record_question_added(db: Session, exam: Exam, question) -> None:
    """
    Chame após db.flush() da Question, antes do commit() da rota.
    Incrementa submitted e recalcula status.
    """
    quota = _get_quota(db, exam.id, question.discipline_id)
    prog = _get_or_create_progress(
        db,
        exam_id=exam.id,
        teacher_user_id=question.author_user_id,
        discipline_id=question.discipline_id,
        class_id=question.class_id,
        quota=quota,
    )
    prog.quota = quota
    prog.submitted += 1
    prog.recalculate_status()
    db.add(prog)
    _append_log(db, prog, ProgressLogEvent.QUESTION_ADDED, question_id=question.id)


def record_question_removed(db: Session, exam: Exam, question) -> None:
    """
    Chame ao deletar uma questão, antes do commit() da rota.
    submitted nunca fica negativo.
    """
    quota = _get_quota(db, exam.id, question.discipline_id)
    prog = _get_or_create_progress(
        db,
        exam_id=exam.id,
        teacher_user_id=question.author_user_id,
        discipline_id=question.discipline_id,
        class_id=question.class_id,
        quota=quota,
    )
    prog.quota = quota
    prog.submitted = max(0, prog.submitted - 1)
    prog.recalculate_status()
    db.add(prog)
    _append_log(db, prog, ProgressLogEvent.QUESTION_REMOVED, question_id=question.id)


def sync_quota_change(
    db: Session,
    exam_id: int,
    discipline_id: int,
    new_quota: int,
) -> None:
    """
    Atualiza todos os registros de progresso da disciplina após mudança
    de cota. Chame dentro de set_quotas, antes do commit().
    """
    rows = db.query(ExamTeacherProgress).filter_by(
        exam_id=exam_id,
        discipline_id=discipline_id,
    ).all()

    for prog in rows:
        old_quota = prog.quota
        prog.quota = new_quota
        prog.recalculate_status()
        db.add(prog)
        _append_log(
            db, prog,
            ProgressLogEvent.QUOTA_CHANGED,
            quota_before=old_quota,
            quota_after=new_quota,
        )
