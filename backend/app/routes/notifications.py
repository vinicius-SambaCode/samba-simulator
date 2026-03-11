# app/routes/notifications.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import require_role, get_current_user
from app.models.base_models import User
from app.models.exam import Exam, ExamStatus, ExamTeacherAssignment, ExamDisciplineQuota, Question

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", dependencies=[Depends(require_role("COORDINATOR", "ADMIN", "TEACHER"))])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_roles = {r.name for r in current_user.roles}
    notifications = []

    if "COORDINATOR" in user_roles or "ADMIN" in user_roles:
        # Simulados em coleta — verifica progresso
        collecting = db.query(Exam).filter(Exam.status == ExamStatus.COLLECTING).all()
        for exam in collecting:
            quotas = {q.discipline_id: q.quota for q in exam.discipline_quotas}
            if not quotas:
                continue

            total_quota = sum(quotas.values())
            submitted = (
                db.query(Question)
                .filter(
                    Question.exam_id == exam.id,
                    Question.state.in_(("submitted", "approved")),
                )
                .count()
            )

            if total_quota > 0 and submitted >= total_quota:
                notifications.append({
                    "id": f"ready_{exam.id}",
                    "type": "ready_to_lock",
                    "exam_id": exam.id,
                    "title": exam.title,
                    "message": f'"{exam.title}" está completo e pronto para ser travado.',
                })
            elif submitted > 0:
                remaining = total_quota - submitted
                notifications.append({
                    "id": f"progress_{exam.id}",
                    "type": "submitted",
                    "exam_id": exam.id,
                    "title": exam.title,
                    "message": f'"{exam.title}" recebeu questões. Faltam {remaining}.',
                })

    if "TEACHER" in user_roles:
        # Assignments pendentes do professor
        assignments = (
            db.query(ExamTeacherAssignment)
            .filter(ExamTeacherAssignment.teacher_user_id == current_user.id)
            .all()
        )
        exam_ids = list({a.exam_id for a in assignments})
        exams = db.query(Exam).filter(
            Exam.id.in_(exam_ids),
            Exam.status == ExamStatus.COLLECTING,
        ).all()

        for exam in exams:
            quotas = {q.discipline_id: q.quota for q in exam.discipline_quotas}
            total_quota = sum(quotas.values())
            submitted = (
                db.query(Question)
                .filter(
                    Question.exam_id == exam.id,
                    Question.author_user_id == current_user.id,
                    Question.state.in_(("submitted", "approved")),
                )
                .count()
            )
            if submitted < total_quota:
                notifications.append({
                    "id": f"pending_{exam.id}",
                    "type": "pending_questions",
                    "exam_id": exam.id,
                    "title": exam.title,
                    "message": f'Você tem questões pendentes em "{exam.title}".',
                })

    return notifications