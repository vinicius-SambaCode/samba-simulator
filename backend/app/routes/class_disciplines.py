# -*- coding: utf-8 -*-
"""
routes/class_disciplines.py
=============================
CRUD da grade curricular por turma (class_disciplines).

Endpoints:
  GET    /school/classes/{class_id}/disciplines          → lista disciplinas da turma
  POST   /school/classes/{class_id}/disciplines          → adiciona disciplina à turma
  DELETE /school/classes/{class_id}/disciplines/{disc_id} → remove disciplina da turma
  PUT    /school/classes/{class_id}/disciplines           → substitui toda a grade (bulk)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.core.deps import require_role
from app.core.security import get_current_user
from app.models.school import SchoolClass, ClassDiscipline
from app.models.models import Discipline
from app.models.base_models import User

router = APIRouter(prefix="/school", tags=["class-disciplines"])


# ── helpers ──────────────────────────────────────────────────────────────────

def _get_class_or_404(db: Session, class_id: int) -> SchoolClass:
    cls = db.get(SchoolClass, class_id)
    if not cls:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    return cls


def _get_discipline_or_404(db: Session, discipline_id: int) -> Discipline:
    disc = db.get(Discipline, discipline_id)
    if not disc:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")
    return disc


def _discipline_out(disc: Discipline) -> dict:
    return {"id": disc.id, "name": disc.name}


# ── GET: listar disciplinas de uma turma ─────────────────────────────────────

@router.get(
    "/classes/{class_id}/disciplines",
    summary="Listar disciplinas da grade curricular de uma turma",
)
def list_class_disciplines(
    class_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    _get_class_or_404(db, class_id)
    links = (
        db.query(ClassDiscipline)
        .filter(ClassDiscipline.class_id == class_id)
        .all()
    )
    disciplines = []
    for link in links:
        disc = db.get(Discipline, link.discipline_id)
        if disc:
            disciplines.append(_discipline_out(disc))
    return disciplines


# ── POST: adicionar disciplina à turma ───────────────────────────────────────

@router.post(
    "/classes/{class_id}/disciplines",
    status_code=201,
    dependencies=[Depends(require_role("COORDINATOR", "ADMIN"))],
    summary="Adicionar disciplina à grade curricular de uma turma",
)
def add_class_discipline(
    class_id: int,
    body: dict,          # {"discipline_id": int}
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    discipline_id = body.get("discipline_id")
    if not discipline_id:
        raise HTTPException(status_code=422, detail="discipline_id é obrigatório")

    _get_class_or_404(db, class_id)
    disc = _get_discipline_or_404(db, discipline_id)

    exists = db.query(ClassDiscipline).filter_by(
        class_id=class_id, discipline_id=discipline_id
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="Disciplina já faz parte da grade desta turma")

    db.add(ClassDiscipline(class_id=class_id, discipline_id=discipline_id))
    db.commit()
    return _discipline_out(disc)


# ── DELETE: remover disciplina da turma ──────────────────────────────────────

@router.delete(
    "/classes/{class_id}/disciplines/{discipline_id}",
    status_code=204,
    dependencies=[Depends(require_role("COORDINATOR", "ADMIN"))],
    summary="Remover disciplina da grade curricular de uma turma",
)
def remove_class_discipline(
    class_id: int,
    discipline_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    link = db.query(ClassDiscipline).filter_by(
        class_id=class_id, discipline_id=discipline_id
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada na grade desta turma")
    db.delete(link)
    db.commit()
    return None


# ── PUT: substituir toda a grade (bulk replace) ──────────────────────────────

@router.put(
    "/classes/{class_id}/disciplines",
    dependencies=[Depends(require_role("COORDINATOR", "ADMIN"))],
    summary="Substituir toda a grade curricular de uma turma (bulk)",
)
def set_class_disciplines(
    class_id: int,
    body: dict,          # {"discipline_ids": [int, ...]}
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    discipline_ids: list[int] = body.get("discipline_ids", [])

    _get_class_or_404(db, class_id)

    # Validar todos os IDs antes de alterar
    disciplines = []
    for did in discipline_ids:
        disciplines.append(_get_discipline_or_404(db, did))

    # Remover grade atual
    db.query(ClassDiscipline).filter_by(class_id=class_id).delete()

    # Inserir nova grade
    for disc in disciplines:
        db.add(ClassDiscipline(class_id=class_id, discipline_id=disc.id))

    db.commit()
    return [_discipline_out(d) for d in disciplines]
