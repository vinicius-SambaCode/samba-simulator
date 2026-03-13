# -*- coding: utf-8 -*-
"""
app/routes/questions_crud.py  — Passo 12
==========================================
CRUD completo de questões + upload (.docx/.txt/.pdf) com imagens.
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
from app.services.progress_service import record_question_added, record_question_removed

router = APIRouter(prefix="/exams", tags=["questions"])
_ALLOWED_EXTENSIONS = {".docx", ".txt", ".pdf"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_exam_or_404(db, exam_id):
    exam = db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(404, "Simulado não encontrado.")
    return exam


def _get_question_or_404(db, exam_id, question_id):
    q = db.query(Question).filter_by(id=question_id, exam_id=exam_id).first()
    if not q:
        raise HTTPException(404, "Questão não encontrada.")
    return q


def _assert_collecting(exam):
    if exam.status != ExamStatus.COLLECTING:
        raise HTTPException(400, f"Simulado em status '{exam.status}' — operação inválida.")


def _get_quota_info(db, exam_id, discipline_id, class_id, author_user_id):
    """Retorna (quota, já_enviadas). quota=0 significa sem limite configurado.
    Conta questões do professor para a disciplina em QUALQUER turma do exame,
    pois o conjunto de questões é compartilhado entre turmas."""
    from app.models.exam import ExamDisciplineQuota, Question
    quota_row = db.query(ExamDisciplineQuota).filter_by(
        exam_id=exam_id, discipline_id=discipline_id
    ).first()
    quota = quota_row.quota if quota_row else 0
    if quota == 0:
        return 0, 0
    # Conta todas as questões do professor para esta disciplina no exame,
    # independente da turma — evita que o mesmo conteúdo seja enviado duplicado
    submitted = db.query(Question).filter_by(
        exam_id=exam_id,
        discipline_id=discipline_id,
        author_user_id=author_user_id,
    ).filter(Question.state.in_(["SUBMITTED", "APPROVED", "submitted", "approved"])).count()
    return quota, submitted


def _assert_quota_not_exceeded(db, exam, discipline_id, class_id, author_user_id, adding=1):
    """Lança 400 se o professor já atingiu ou vai exceder a cota."""
    quota, submitted = _get_quota_info(db, exam.id, discipline_id, class_id, author_user_id)
    if quota > 0 and submitted + adding > quota:
        disponivel = max(0, quota - submitted)
        raise HTTPException(
            400,
            f"Cota excedida: você pode enviar ainda {disponivel} questão(ões) "
            f"(cota={quota}, já enviadas={submitted}, tentando adicionar={adding})."
        )


def _assert_can_edit(question, current_user):
    roles = {r.name for r in getattr(current_user, "roles", [])}
    if question.author_user_id != current_user.id and "COORDINATOR" not in roles:
        raise HTTPException(403, "Você não pode editar a questão de outro professor.")


def _assert_teacher_assigned(db, exam, current_user, class_id, discipline_id):
    ok = db.query(ExamTeacherAssignment).filter_by(
        exam_id=exam.id, class_id=class_id,
        discipline_id=discipline_id, teacher_user_id=current_user.id,
    ).first()
    if not ok:
        raise HTTPException(403, "Você não está atribuído a esta turma/disciplina.")


def _validate_options(exam, labels):
    needed = {"A","B","C","D"} if exam.options_count == 4 else {"A","B","C","D","E"}
    if labels != needed:
        raise HTTPException(400, f"Alternativas inválidas: esperado {sorted(needed)}, recebido {sorted(labels)}.")


def _upsert_link(db, exam, question_id, correct_label):
    from sqlalchemy import func
    link = db.query(ExamQuestionLink).filter_by(exam_id=exam.id, question_id=question_id).first()
    if link:
        if correct_label:
            link.correct_label = correct_label; db.add(link)
        else:
            db.delete(link)
    elif correct_label:
        mx = db.query(func.max(ExamQuestionLink.order_idx)).filter_by(exam_id=exam.id).scalar()
        db.add(ExamQuestionLink(exam_id=exam.id, question_id=question_id,
                                order_idx=(mx or 0)+1, correct_label=correct_label))


def _q_dict(q, include_images=False, correct_label=None):
    d = {
        "id": q.id, "exam_id": q.exam_id,
        "discipline_id": q.discipline_id, "class_id": q.class_id,
        "author_user_id": q.author_user_id, "source": q.source,
        "state": q.state, "stem": q.stem, "has_images": q.has_images,
        "correct_label": correct_label,
        "options": [{"label": o.label, "text": o.text}
                    for o in sorted(q.options, key=lambda x: x.label)],
    }
    if include_images and hasattr(q, "images"):
        d["images"] = [
            {"id": img.id, "url": img.url_path(), "context": img.context,
             "order_idx": img.order_idx, "mime_type": img.mime_type,
             "width_px": img.width_px, "height_px": img.height_px}
            for img in sorted(q.images, key=lambda x: (x.context, x.order_idx))
        ]
    return d


# ---------------------------------------------------------------------------
# GET /exams/{exam_id}/questions
# ---------------------------------------------------------------------------

@router.get("/{exam_id}/questions")
def list_questions(
    exam_id: int,
    class_id: Optional[int] = Query(None),
    discipline_id: Optional[int] = Query(None),
    state: Optional[str] = Query(None),
    author_user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_exam_or_404(db, exam_id)
    roles = {r.name for r in getattr(current_user, "roles", [])}
    is_coord = "COORDINATOR" in roles

    q = db.query(Question).filter(Question.exam_id == exam_id)
    if not is_coord:
        q = q.filter(Question.author_user_id == current_user.id)
    if class_id:      q = q.filter(Question.class_id == class_id)
    if discipline_id: q = q.filter(Question.discipline_id == discipline_id)
    if state:         q = q.filter(Question.state == state)
    if author_user_id and is_coord:
        q = q.filter(Question.author_user_id == author_user_id)

    questions = q.order_by(Question.id).all()
    links = {
        lnk.question_id: lnk.correct_label
        for lnk in db.query(ExamQuestionLink).filter_by(exam_id=exam_id).all()
    }
    return [_q_dict(q, include_images=True, correct_label=links.get(q.id)) for q in questions]


# ---------------------------------------------------------------------------
# GET /exams/{exam_id}/questions/{question_id}
# ---------------------------------------------------------------------------

@router.get("/{exam_id}/questions/{question_id}")
def get_question(
    exam_id: int, question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_exam_or_404(db, exam_id)
    q = _get_question_or_404(db, exam_id, question_id)
    roles = {r.name for r in getattr(current_user, "roles", [])}
    if q.author_user_id != current_user.id and "COORDINATOR" not in roles:
        raise HTTPException(403, "Acesso negado.")
    link = db.query(ExamQuestionLink).filter_by(exam_id=exam_id, question_id=question_id).first()
    return _q_dict(q, include_images=True, correct_label=link.correct_label if link else None)



# ---------------------------------------------------------------------------
# POST /exams/{exam_id}/questions  — criação manual de questão
# ---------------------------------------------------------------------------

@router.post("/{exam_id}/questions", dependencies=[Depends(require_role("TEACHER"))])
def create_question(
    exam_id: int, payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exam = _get_exam_or_404(db, exam_id)
    _assert_collecting(exam)

    class_id      = payload.get("class_id")
    discipline_id = payload.get("discipline_id")
    if class_id and discipline_id:
        _assert_teacher_assigned(db, exam, current_user, class_id, discipline_id)

    stem = (payload.get("stem") or "").strip()
    if not stem:
        raise HTTPException(400, "Enunciado obrigatório.")

    # Validação de cota
    if class_id and discipline_id:
        _assert_quota_not_exceeded(db, exam, discipline_id, class_id, current_user.id, adding=1)

    options = payload.get("options") or []
    _validate_options(exam, {o["label"].upper() for o in options})

    q = Question(
        exam_id=exam_id,
        author_user_id=current_user.id,
        discipline_id=discipline_id,
        class_id=class_id,
        stem=stem,
        source="manual",
        state="submitted",
        has_images=False,
    )
    db.add(q)
    db.flush()

    for o in options:
        db.add(QuestionOption(
            question_id=q.id,
            label=o["label"].strip().upper(),
            text=o["text"].strip(),
        ))

    correct_label = payload.get("correct_label")
    if correct_label:
        _upsert_link(db, exam, q.id, correct_label.strip().upper())

    record_question_added(db, exam, q)
    db.commit()
    db.refresh(q)

    link = db.query(ExamQuestionLink).filter_by(exam_id=exam_id, question_id=q.id).first()
    return _q_dict(q, include_images=True, correct_label=link.correct_label if link else None)


# ---------------------------------------------------------------------------
# PATCH /exams/{exam_id}/questions/{question_id}
# ---------------------------------------------------------------------------

@router.patch("/{exam_id}/questions/{question_id}")
def update_question(
    exam_id: int, question_id: int, payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exam = _get_exam_or_404(db, exam_id)
    roles = {r.name for r in getattr(current_user, "roles", [])}
    is_coord = "COORDINATOR" in roles

    # COORDINATOR pode editar gabarito em qualquer status do simulado
    # Professor só pode editar enquanto está em coleta
    only_correct_label = (
        set(payload.keys()) - {"correct_label"}
    ) == set()

    if not (is_coord and only_correct_label):
        _assert_collecting(exam)

    q = _get_question_or_404(db, exam_id, question_id)
    _assert_can_edit(q, current_user)

    if "stem" in payload and payload["stem"]:
        q.stem = payload["stem"].strip()

    if "options" in payload and payload["options"]:
        opts = payload["options"]
        _validate_options(exam, {o["label"].upper() for o in opts})
        db.query(QuestionOption).filter_by(question_id=q.id).delete()
        db.flush()
        for o in opts:
            db.add(QuestionOption(question_id=q.id,
                                  label=o["label"].strip().upper(),
                                  text=o["text"].strip()))

    if "correct_label" in payload:
        cl = payload["correct_label"]
        _upsert_link(db, exam, q.id, cl.strip().upper() if cl else None)

    db.add(q); db.commit(); db.refresh(q)
    link = db.query(ExamQuestionLink).filter_by(exam_id=exam_id, question_id=question_id).first()
    return _q_dict(q, include_images=True, correct_label=link.correct_label if link else None)


# ---------------------------------------------------------------------------
# DELETE /exams/{exam_id}/questions/{question_id}
# ---------------------------------------------------------------------------

@router.delete("/{exam_id}/questions/{question_id}")
def delete_question(
    exam_id: int, question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exam = _get_exam_or_404(db, exam_id)
    _assert_collecting(exam)

    q = _get_question_or_404(db, exam_id, question_id)
    _assert_can_edit(q, current_user)

    if hasattr(q, "images"):
        import os
        for img in q.images:
            p = img.absolute_path()
            if os.path.exists(p):
                os.remove(p)

    record_question_removed(db, exam, q)
    db.query(ExamQuestionLink).filter_by(exam_id=exam_id, question_id=question_id).delete()
    db.delete(q); db.commit()
    return {"detail": "Questão removida.", "question_id": question_id}


# ---------------------------------------------------------------------------
# POST /exams/{exam_id}/questions/upload
# ---------------------------------------------------------------------------

@router.post("/{exam_id}/questions/upload", dependencies=[Depends(require_role("TEACHER"))])
async def upload_questions(
    exam_id: int,
    class_id: int = Form(...),
    discipline_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exam = _get_exam_or_404(db, exam_id)
    _assert_collecting(exam)
    _assert_teacher_assigned(db, exam, current_user, class_id, discipline_id)

    filename = (file.filename or "").lower()
    ext = next((e for e in _ALLOWED_EXTENSIONS if filename.endswith(e)), "")
    if not ext:
        raise HTTPException(400, f"Formato não suportado. Use: {', '.join(sorted(_ALLOWED_EXTENSIONS))}")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(400, "Arquivo vazio.")

    try:
        if ext == ".docx":   text = extract_text_from_docx(file_bytes)
        elif ext == ".pdf":  text = extract_text_from_pdf(file_bytes)
        else:                text = extract_text_from_txt(file_bytes)
    except Exception as e:
        raise HTTPException(422, f"Erro ao ler arquivo: {e}")

    try:
        parsed = parse_text_to_questions(text)
    except ValueError as e:
        raise HTTPException(422, f"Erro no formato: {e}")

    if not parsed:
        raise HTTPException(422, "Nenhuma questão encontrada no arquivo.")

    # Validação de cota antes de inserir
    _assert_quota_not_exceeded(db, exam, discipline_id, class_id, current_user.id, adding=len(parsed))

    # Extrai imagens do docx agrupadas por questão (por posição no XML)
    images_by_q: dict = {}
    if ext == ".docx":
        try:
            from app.services.docx_image_extractor import extract_images_by_question as _extract_imgs
            images_by_q = _extract_imgs(file_bytes)
        except Exception:
            pass

    created_ids, skipped, total_images = [], 0, 0
    q_idx = 0  # índice da questão válida (0-based, alinhado com images_by_q)

    for idx, item in enumerate(parsed):
        opts = [{"label": o["label"].strip().upper(), "text": o["text"].strip()}
                for o in item["options"]]
        try:
            _validate_options(exam, {o["label"] for o in opts})
        except HTTPException:
            skipped += 1
            q_idx += 1
            continue

        q_imgs_for_this = images_by_q.get(q_idx, [])

        q = Question(
            exam_id=exam.id, discipline_id=discipline_id,
            class_id=class_id, author_user_id=current_user.id,
            source={"docx": "docx", ".pdf": "pdf"}.get(ext, "txt"),
            state="submitted", stem=item["stem"],
            has_images=bool(q_imgs_for_this),
        )
        db.add(q); db.flush()

        for o in opts:
            db.add(QuestionOption(question_id=q.id, label=o["label"], text=o["text"]))

        correct = item.get("correct_label")
        if correct and exam.answer_source == AnswerSource.TEACHERS:
            correct = correct.strip().upper()
            if correct in {o["label"] for o in opts}:
                _upsert_link(db, exam, q.id, correct)

        # Salva imagens vinculadas a esta questão específica
        if q_imgs_for_this:
            try:
                from app.services.docx_image_extractor import save_images_to_disk
                from app.models.exam import QuestionImage  # type: ignore
                saved = save_images_to_disk(q.id, q_imgs_for_this)
                for s in saved:
                    db.add(QuestionImage(
                        question_id=q.id,
                        storage_path=s["storage_path"],
                        mime_type=s["mime_type"],
                        context=s["context"],
                        order_idx=s["order_idx"],
                        width_px=s["width_px"],
                        height_px=s["height_px"],
                    ))
                total_images += len(saved)
            except Exception:
                pass

        record_question_added(db, exam, q)
        created_ids.append(q.id)
        q_idx += 1

    db.commit()
    return {
        "detail":       f"{len(created_ids)} questão(ões) importada(s).",
        "created":      len(created_ids),
        "skipped":      skipped,
        "images_saved": total_images,
        "question_ids": created_ids,
    }


# ---------------------------------------------------------------------------
# POST /exams/{exam_id}/questions/{question_id}/images
# Upload de imagem avulsa para questão manual (enunciado ou alternativa)
# ---------------------------------------------------------------------------

_ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}

@router.post("/{exam_id}/questions/{question_id}/images", dependencies=[Depends(require_role("TEACHER"))])
async def upload_question_image(
    exam_id: int,
    question_id: int,
    context: str = Form("stem"),   # "stem" | "option_A" | "option_B" ...
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Faz upload de uma imagem para o enunciado ou alternativa de uma questão manual."""
    exam = _get_exam_or_404(db, exam_id)
    _assert_collecting(exam)
    q = _get_question_or_404(db, exam_id, question_id)
    _assert_can_edit(q, current_user)

    filename = (file.filename or "").lower()
    ext = next((e for e in _ALLOWED_IMAGE_EXTENSIONS if filename.endswith(e)), "")
    if not ext:
        raise HTTPException(400, f"Formato não suportado. Use: {', '.join(sorted(_ALLOWED_IMAGE_EXTENSIONS))}")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(400, "Arquivo vazio.")
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(400, "Imagem muito grande. Máximo: 10 MB.")

    # Detecta dimensões
    width_px = height_px = None
    try:
        import io as _io
        from PIL import Image as _PIL
        with _PIL.open(_io.BytesIO(file_bytes)) as im:
            width_px, height_px = im.size
    except Exception:
        pass

    # Salva em disco
    import uuid, os
    from app.models.exam import QuestionImage

    storage_base = os.environ.get("STORAGE_DIR", "/app/storage")
    folder = os.path.join(storage_base, "questions", str(question_id))
    os.makedirs(folder, exist_ok=True)

    safe_ext = ext.lstrip(".")
    if safe_ext == "jpg":
        safe_ext = "jpeg"
    unique_name = f"img_{context}_{uuid.uuid4().hex[:8]}.{safe_ext}"
    abs_path = os.path.join(folder, unique_name)

    with open(abs_path, "wb") as f:
        f.write(file_bytes)

    storage_path = f"questions/{question_id}/{unique_name}"
    mime_type = f"image/{safe_ext}"

    # Determina order_idx (próximo na sequência do mesmo context)
    from sqlalchemy import func
    max_idx = db.query(func.max(QuestionImage.order_idx)).filter_by(
        question_id=question_id, context=context
    ).scalar()
    order_idx = (max_idx or -1) + 1

    img = QuestionImage(
        question_id=question_id,
        storage_path=storage_path,
        mime_type=mime_type,
        context=context,
        order_idx=order_idx,
        width_px=width_px,
        height_px=height_px,
    )
    db.add(img)
    q.has_images = True
    db.add(q)
    db.commit()
    db.refresh(img)

    return {
        "id":           img.id,
        "url":          img.url_path(),
        "context":      img.context,
        "order_idx":    img.order_idx,
        "mime_type":    img.mime_type,
        "width_px":     img.width_px,
        "height_px":    img.height_px,
    }


# ---------------------------------------------------------------------------
# DELETE /exams/{exam_id}/questions/{question_id}/images/{image_id}
# ---------------------------------------------------------------------------

@router.delete("/{exam_id}/questions/{question_id}/images/{image_id}", dependencies=[Depends(require_role("TEACHER"))])
def delete_question_image(
    exam_id: int, question_id: int, image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.exam import QuestionImage
    import os

    exam = _get_exam_or_404(db, exam_id)
    _assert_collecting(exam)
    q = _get_question_or_404(db, exam_id, question_id)
    _assert_can_edit(q, current_user)

    img = db.query(QuestionImage).filter_by(id=image_id, question_id=question_id).first()
    if not img:
        raise HTTPException(404, "Imagem não encontrada.")

    abs_path = img.absolute_path()
    if os.path.exists(abs_path):
        os.remove(abs_path)

    db.delete(img)

    # Atualiza has_images se não sobrou nenhuma
    remaining = db.query(QuestionImage).filter_by(question_id=question_id).count()
    if remaining == 0:
        q.has_images = False
        db.add(q)

    db.commit()
    return {"detail": "Imagem removida.", "image_id": image_id}