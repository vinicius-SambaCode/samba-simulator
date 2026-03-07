# -*- coding: utf-8 -*-
"""
app/routes/questions_crud.py
==============================
CRUD completo de questões + upload de arquivo (.docx / .txt / .pdf).

ENDPOINTS
---------
GET    /exams/{exam_id}/questions
    Lista questões do simulado.
    Filtros: class_id, discipline_id, state, author_user_id
    Acesso: TEACHER (só vê as próprias) | COORDINATOR (vê todas)

GET    /exams/{exam_id}/questions/{question_id}
    Detalhe de uma questão com alternativas.

PATCH  /exams/{exam_id}/questions/{question_id}
    Edita enunciado, alternativas e/ou gabarito.
    Regras:
      - Apenas o autor ou COORDINATOR pode editar.
      - Só permitido em status COLLECTING.
      - Se alternativas forem enviadas, substituem todas as existentes.
      - Se correct_label vier, atualiza ExamQuestionLink.

DELETE /exams/{exam_id}/questions/{question_id}
    Remove questão + opções + link de seleção.
    Atualiza ExamTeacherProgress via progress_service.
    Regras:
      - Apenas o autor ou COORDINATOR pode deletar.
      - Só permitido em status COLLECTING.

POST   /exams/{exam_id}/questions/upload
    Upload de arquivo (.docx, .txt, .pdf).
    Form fields: file, class_id, discipline_id
    Retorna lista de questões criadas com IDs e contadores.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import require_role
from app.core.security import get_current_user
from app.models.base_models import User
from app.models.exam import (
    Exam, ExamStatus, AnswerSource,
    Question, QuestionOption, ExamQuestionLink,
    ExamTeacherAssignment,
)
from app.services.question_parser import (
    parse_text_to_questions,
    extract_text_from_docx,
    extract_text_from_pdf,
    extract_text_from_txt,
)
from app.services.progress_service import (
    record_question_added,
    record_question_removed,
)

router = APIRouter(prefix="/exams", tags=["questions"])

_ALLOWED_EXTENSIONS = {".docx", ".txt", ".pdf"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_exam_or_404(db: Session, exam_id: int) -> Exam:
    exam = db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Simulado não encontrado.")
    return exam


def _get_question_or_404(db: Session, exam_id: int, question_id: int) -> Question:
    q = db.query(Question).filter_by(id=question_id, exam_id=exam_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Questão não encontrada.")
    return q


def _assert_collecting(exam: Exam) -> None:
    if exam.status != ExamStatus.COLLECTING:
        raise HTTPException(
            status_code=400,
            detail=f"Operação inválida: simulado está em status '{exam.status}'."
        )


def _assert_can_edit(question: Question, current_user: User) -> None:
    """Permite edição apenas ao autor ou a COORDINATOR."""
    user_roles = {r.name for r in getattr(current_user, "roles", [])}
    if question.author_user_id != current_user.id and "COORDINATOR" not in user_roles:
        raise HTTPException(status_code=403, detail="Você não pode editar a questão de outro professor.")


def _assert_teacher_assigned(db: Session, exam: Exam, current_user: User, class_id: int, discipline_id: int) -> None:
    assign = db.query(ExamTeacherAssignment).filter_by(
        exam_id=exam.id,
        class_id=class_id,
        discipline_id=discipline_id,
        teacher_user_id=current_user.id,
    ).first()
    if not assign:
        raise HTTPException(status_code=403, detail="Você não está atribuído a esta turma/disciplina no simulado.")


def _validate_options_count(exam: Exam, labels: set) -> None:
    needed = {"A", "B", "C", "D"} if exam.options_count == 4 else {"A", "B", "C", "D", "E"}
    if labels != needed:
        raise HTTPException(
            status_code=400,
            detail=f"Alternativas inválidas: esperado {sorted(needed)}, recebido {sorted(labels)}."
        )


def _update_selection_link(db: Session, exam: Exam, question_id: int, correct_label: Optional[str]) -> None:
    """Cria ou atualiza ExamQuestionLink com o gabarito."""
    from sqlalchemy import func
    link = db.query(ExamQuestionLink).filter_by(exam_id=exam.id, question_id=question_id).first()
    if link:
        if correct_label:
            link.correct_label = correct_label
            db.add(link)
        elif correct_label is None:
            # Se vier explicitamente None, remove o link
            db.delete(link)
    else:
        if correct_label:
            max_order = db.query(func.max(ExamQuestionLink.order_idx)).filter(
                ExamQuestionLink.exam_id == exam.id
            ).scalar()
            order_idx = (max_order or 0) + 1
            db.add(ExamQuestionLink(
                exam_id=exam.id,
                question_id=question_id,
                order_idx=order_idx,
                correct_label=correct_label,
            ))


def _question_to_dict(q: Question) -> dict:
    return {
        "id":            q.id,
        "exam_id":       q.exam_id,
        "discipline_id": q.discipline_id,
        "class_id":      q.class_id,
        "author_user_id": q.author_user_id,
        "source":        q.source,
        "state":         q.state,
        "stem":          q.stem,
        "has_images":    q.has_images,
        "options": [
            {"label": o.label, "text": o.text}
            for o in sorted(q.options, key=lambda x: x.label)
        ],
    }


# ---------------------------------------------------------------------------
# GET /exams/{exam_id}/questions
# ---------------------------------------------------------------------------

@router.get("/{exam_id}/questions")
def list_questions(
    exam_id: int,
    class_id:        Optional[int] = Query(None),
    discipline_id:   Optional[int] = Query(None),
    state:           Optional[str] = Query(None),
    author_user_id:  Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exam = _get_exam_or_404(db, exam_id)

    user_roles = {r.name for r in getattr(current_user, "roles", [])}
    is_coord = "COORDINATOR" in user_roles

    q = db.query(Question).filter(Question.exam_id == exam_id)

    # Professor só vê as próprias questões
    if not is_coord:
        q = q.filter(Question.author_user_id == current_user.id)

    if class_id:
        q = q.filter(Question.class_id == class_id)
    if discipline_id:
        q = q.filter(Question.discipline_id == discipline_id)
    if state:
        q = q.filter(Question.state == state)
    if author_user_id and is_coord:
        q = q.filter(Question.author_user_id == author_user_id)

    questions = q.order_by(Question.id.asc()).all()
    return [_question_to_dict(q) for q in questions]


# ---------------------------------------------------------------------------
# GET /exams/{exam_id}/questions/{question_id}
# ---------------------------------------------------------------------------

@router.get("/{exam_id}/questions/{question_id}")
def get_question(
    exam_id: int,
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exam = _get_exam_or_404(db, exam_id)
    q = _get_question_or_404(db, exam_id, question_id)

    user_roles = {r.name for r in getattr(current_user, "roles", [])}
    if q.author_user_id != current_user.id and "COORDINATOR" not in user_roles:
        raise HTTPException(status_code=403, detail="Acesso negado.")

    # Inclui gabarito se existir link
    link = db.query(ExamQuestionLink).filter_by(exam_id=exam_id, question_id=question_id).first()
    result = _question_to_dict(q)
    result["correct_label"] = link.correct_label if link else None
    return result


# ---------------------------------------------------------------------------
# PATCH /exams/{exam_id}/questions/{question_id}
# ---------------------------------------------------------------------------

@router.patch("/{exam_id}/questions/{question_id}")
def update_question(
    exam_id: int,
    question_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Payload aceita qualquer combinação de:
    {
      "stem": "Novo enunciado",
      "options": [{"label": "A", "text": "..."}, ...],
      "correct_label": "C"
    }
    Se 'options' vier, substitui TODAS as alternativas existentes.
    """
    exam = _get_exam_or_404(db, exam_id)
    _assert_collecting(exam)
    q = _get_question_or_404(db, exam_id, question_id)
    _assert_can_edit(q, current_user)

    # Atualiza enunciado
    if "stem" in payload and payload["stem"]:
        q.stem = payload["stem"].strip()

    # Substitui alternativas
    if "options" in payload and payload["options"]:
        opts = payload["options"]
        labels = {o["label"].upper() for o in opts}
        _validate_options_count(exam, labels)

        # Remove antigas
        db.query(QuestionOption).filter_by(question_id=q.id).delete()
        db.flush()

        # Cria novas
        for o in opts:
            db.add(QuestionOption(
                question_id=q.id,
                label=o["label"].strip().upper(),
                text=o["text"].strip(),
            ))

    # Atualiza gabarito
    if "correct_label" in payload:
        cl = payload["correct_label"]
        if cl:
            cl = cl.strip().upper()
        _update_selection_link(db, exam, q.id, cl if cl else None)

    db.add(q)
    db.commit()
    db.refresh(q)

    link = db.query(ExamQuestionLink).filter_by(exam_id=exam_id, question_id=question_id).first()
    result = _question_to_dict(q)
    result["correct_label"] = link.correct_label if link else None
    return result


# ---------------------------------------------------------------------------
# DELETE /exams/{exam_id}/questions/{question_id}
# ---------------------------------------------------------------------------

@router.delete("/{exam_id}/questions/{question_id}")
def delete_question(
    exam_id: int,
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exam = _get_exam_or_404(db, exam_id)
    _assert_collecting(exam)
    q = _get_question_or_404(db, exam_id, question_id)
    _assert_can_edit(q, current_user)

    # Atualiza progresso antes de deletar
    record_question_removed(db, exam, q)

    # Remove link de seleção se existir
    db.query(ExamQuestionLink).filter_by(exam_id=exam_id, question_id=question_id).delete()

    db.delete(q)
    db.commit()
    return {"detail": "Questão removida.", "question_id": question_id}


# ---------------------------------------------------------------------------
# POST /exams/{exam_id}/questions/upload
# ---------------------------------------------------------------------------

@router.post("/{exam_id}/questions/upload", dependencies=[Depends(require_role("TEACHER"))])
async def upload_questions(
    exam_id:       int,
    class_id:      int      = Form(..., description="ID da turma"),
    discipline_id: int      = Form(..., description="ID da disciplina"),
    file:          UploadFile = File(..., description="Arquivo .docx, .txt ou .pdf"),
    db:            Session  = Depends(get_db),
    current_user:  User     = Depends(get_current_user),
):
    exam = _get_exam_or_404(db, exam_id)
    _assert_collecting(exam)
    _assert_teacher_assigned(db, exam, current_user, class_id, discipline_id)

    # Valida extensão
    filename = (file.filename or "").lower()
    ext = ""
    for allowed in _ALLOWED_EXTENSIONS:
        if filename.endswith(allowed):
            ext = allowed
            break
    if not ext:
        raise HTTPException(
            status_code=400,
            detail=f"Formato não suportado. Use: {', '.join(sorted(_ALLOWED_EXTENSIONS))}"
        )

    # Lê bytes do arquivo
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")

    # Extrai texto
    try:
        if ext == ".docx":
            text = extract_text_from_docx(file_bytes)
        elif ext == ".pdf":
            text = extract_text_from_pdf(file_bytes)
        else:
            text = extract_text_from_txt(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Erro ao ler arquivo: {str(e)}")

    # Parseia questões
    try:
        parsed = parse_text_to_questions(text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro no formato do arquivo: {str(e)}")

    if not parsed:
        raise HTTPException(
            status_code=422,
            detail="Nenhuma questão encontrada no arquivo. Verifique o formato."
        )

    # Cria questões
    created_ids = []
    skipped = 0

    for item in parsed:
        opts = [
            {"label": o["label"].strip().upper(), "text": o["text"].strip()}
            for o in item["options"]
        ]

        # Valida número de alternativas — pula questões inválidas sem abortar
        try:
            labels = {o["label"] for o in opts}
            _validate_options_count(exam, labels)
        except HTTPException:
            skipped += 1
            continue

        q = Question(
            exam_id=exam.id,
            discipline_id=discipline_id,
            class_id=class_id,
            author_user_id=current_user.id,
            source="docx" if ext == ".docx" else ("pdf" if ext == ".pdf" else "txt"),
            state="submitted",
            stem=item["stem"],
            has_images=False,
        )
        db.add(q)
        db.flush()

        for o in opts:
            db.add(QuestionOption(question_id=q.id, label=o["label"], text=o["text"]))

        # Gabarito opcional
        correct = item.get("correct_label")
        if correct and exam.answer_source == AnswerSource.TEACHERS:
            correct = correct.strip().upper()
            if correct in {o["label"] for o in opts}:
                _update_selection_link(db, exam, q.id, correct)

        # Atualiza progresso
        record_question_added(db, exam, q)
        created_ids.append(q.id)

    db.commit()

    return {
        "detail":       f"{len(created_ids)} questão(ões) importada(s).",
        "created":      len(created_ids),
        "skipped":      skipped,
        "question_ids": created_ids,
    }
