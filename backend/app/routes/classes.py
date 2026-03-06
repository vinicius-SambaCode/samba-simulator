# -*- coding: utf-8 -*-
"""
Rotas (CRUD simples) para a camada escolar:
- /school/grades
- /school/sections
- /school/classes

Apenas COORDINATOR pode criar/editar estruturas de escola.
GETs podem ser abertos a TEACHER, conforme sua política (aqui deixei autenticado).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user
from app.core.deps import require_role
from app.models.base_models import User
from app.models.school import SchoolGrade, ClassSection, SchoolClass
from app.schemas.school import (
    GradeCreate, GradeOut, SectionCreate, SectionOut, ClassCreate, ClassOut
)

router = APIRouter(prefix="/school", tags=["school"])


# ------------ Grades ------------
@router.post("/grades", response_model=GradeOut, dependencies=[Depends(require_role("COORDINATOR"))])
def create_grade(data: GradeCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    exists = db.query(SchoolGrade).filter(
        SchoolGrade.level == data.level,
        SchoolGrade.year_number == data.year_number
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="Já existe esta série/ano neste nível.")

    grade = SchoolGrade(level=data.level, year_number=data.year_number, label=data.label)
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade


@router.get("/grades", response_model=list[GradeOut])
def list_grades(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Se quiser, filtre por nível/ordem
    rows = db.query(SchoolGrade).order_by(SchoolGrade.level, SchoolGrade.year_number).all()
    return rows


# ------------ Sections ------------
@router.post("/sections", response_model=SectionOut, dependencies=[Depends(require_role("COORDINATOR"))])
def create_section(data: SectionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    label = data.label.strip().upper()
    exists = db.query(ClassSection).filter(ClassSection.label == label).first()
    if exists:
        raise HTTPException(status_code=400, detail="Já existe esta turma/section.")
    sec = ClassSection(label=label)
    db.add(sec)
    db.commit()
    db.refresh(sec)
    return sec


@router.get("/sections", response_model=list[SectionOut])
def list_sections(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(ClassSection).order_by(ClassSection.label).all()
    return rows


# ------------ Classes ------------
@router.post("/classes", response_model=ClassOut, dependencies=[Depends(require_role("COORDINATOR"))])
def create_class(data: ClassCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    grade = db.get(SchoolGrade, data.grade_id)
    sec = db.get(ClassSection, data.section_id)
    if not grade or not sec:
        raise HTTPException(status_code=400, detail="grade_id ou section_id inválidos.")

    # Define name por convenção: f"{grade.label}{sec.label}" (ex: "3ªA", "6ºB")
    name = f"{grade.label}{sec.label}"

    exists = db.query(SchoolClass).filter(
        SchoolClass.grade_id == grade.id,
        SchoolClass.section_id == sec.id
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="Esta classe (série+turma) já existe.")

    sc = SchoolClass(grade_id=grade.id, section_id=sec.id, name=name)
    db.add(sc)
    db.commit()
    db.refresh(sc)
    return sc


@router.get("/classes", response_model=list[ClassOut])
def list_classes(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(SchoolClass).order_by(SchoolClass.name).all()
    return rows
