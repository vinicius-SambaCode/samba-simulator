# app/routes/students.py
# -*- coding: utf-8 -*-
"""
Rotas de Alunos (students)
- POST /school/students        (COORDINATOR) cria aluno
- GET  /school/students        (autenticado) lista alunos (filtros: class_id, ra, name_like)
- GET  /school/students/{id}   (autenticado) detalhe
- PATCH/PUT /school/students/{id} (COORDINATOR) atualiza aluno
- DELETE /school/students/{id} (COORDINATOR) remove aluno

Regras de negócio:
- RA único
- class_id deve existir em school_classes
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.db import get_db
from app.core.security import get_current_user
from app.core.dependencies import require_role
from app.models.base_models import User
from app.models.school import Student, SchoolClass
from app.schemas.student import StudentCreate, StudentUpdate, StudentOut

router = APIRouter(prefix="/school/students", tags=["school"])


def _get_student_or_404(db: Session, student_id: int) -> Student:
    st = db.get(Student, student_id)
    if not st:
        raise HTTPException(status_code=404, detail="Aluno não encontrado.")
    return st


@router.post("/", response_model=StudentOut, dependencies=[Depends(require_role("COORDINATOR"))])
def create_student(
    payload: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # RA único
    exists_ra = db.query(Student).filter(Student.ra == payload.ra).first()
    if exists_ra:
        raise HTTPException(status_code=400, detail="Já existe um aluno com este RA.")

    # Turma válida
    cls = db.get(SchoolClass, payload.class_id)
    if not cls:
        raise HTTPException(status_code=400, detail="Turma (class_id) inválida.")

    st = Student(ra=payload.ra.strip(), name=payload.name.strip(), class_id=payload.class_id)
    db.add(st)
    db.commit()
    db.refresh(st)
    return st


@router.get("/", response_model=List[StudentOut])
def list_students(
    class_id: Optional[int] = Query(None, description="Filtra por turma"),
    ra: Optional[str] = Query(None, description="Filtra por RA exato"),
    name_like: Optional[str] = Query(None, description="Filtra por nome contendo (case-insensitive)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Student)

    if class_id is not None:
        q = q.filter(Student.class_id == class_id)

    if ra:
        q = q.filter(Student.ra == ra)

    if name_like:
        like = f"%{name_like.strip()}%"
        # Para case-insensitive no Postgres: usar ilike
        q = q.filter(Student.name.ilike(like))

    rows = q.order_by(Student.class_id.asc(), Student.name.asc()).all()
    return rows


@router.get("/{student_id}", response_model=StudentOut)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    st = _get_student_or_404(db, student_id)
    return st


@router.patch("/{student_id}", response_model=StudentOut, dependencies=[Depends(require_role("COORDINATOR"))])
def update_student(
    student_id: int,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    st = _get_student_or_404(db, student_id)

    if payload.ra and payload.ra != st.ra:
        conflict = db.query(Student).filter(Student.ra == payload.ra).first()
        if conflict:
            raise HTTPException(status_code=400, detail="Já existe um aluno com este RA.")
        st.ra = payload.ra.strip()

    if payload.name:
        st.name = payload.name.strip()

    if payload.class_id is not None and payload.class_id != st.class_id:
        cls = db.get(SchoolClass, payload.class_id)
        if not cls:
            raise HTTPException(status_code=400, detail="Turma (class_id) inválida.")
        st.class_id = payload.class_id

    db.add(st)
    db.commit()
    db.refresh(st)
    return st


@router.delete("/{student_id}", dependencies=[Depends(require_role("COORDINATOR"))])
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    st = _get_student_or_404(db, student_id)
    db.delete(st)
    db.commit()
    return {"detail": "Aluno removido."}