# backend/app/routes/grade.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.core.security import get_current_user
from app.core.permissions import require_role
from app.models.school import SchoolGrade, EducationLevel
from app.schemas.grade import SchoolGradeCreate, SchoolGradeUpdate, SchoolGradeOut

router = APIRouter(prefix="/grades", tags=["grades"])

# GET /grades/
@router.get("/", response_model=List[SchoolGradeOut])
def list_grades(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(SchoolGrade).all()

# POST /grades/
@router.post(
    "/",
    response_model=SchoolGradeOut,
    dependencies=[Depends(require_role("ADMIN", "COORDINATOR"))]
)
def create_grade(
    data: SchoolGradeCreate,
    db: Session = Depends(get_db),
):
    # Evita duplicidade (level + year_number)
    exists = (
        db.query(SchoolGrade)
        .filter(SchoolGrade.level == data.level, SchoolGrade.year_number == data.year_number)
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Série/ano já existe para este nível")

    g = SchoolGrade(level=data.level, year_number=data.year_number, label=data.label)
    db.add(g); db.commit(); db.refresh(g)
    return g

# PUT /grades/{id}/
@router.put(
    "/{grade_id}/",
    response_model=SchoolGradeOut,
    dependencies=[Depends(require_role("ADMIN", "COORDINATOR"))]
)
def update_grade(
    grade_id: int,
    data: SchoolGradeUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    g = db.get(SchoolGrade, grade_id)
    if not g:
        raise HTTPException(status_code=404, detail="Série não encontrada")

    # Evita duplicidade (level + year_number) com outro id
    exists = (
        db.query(SchoolGrade)
        .filter(
            SchoolGrade.level == data.level,
            SchoolGrade.year_number == data.year_number,
            SchoolGrade.id != grade_id
        )
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Já existe série/ano com estes dados")

    g.level = data.level
    g.year_number = data.year_number
    g.label = data.label

    db.commit(); db.refresh(g)
    return g

# DELETE /grades/{id}/
@router.delete(
    "/{grade_id}/",
    status_code=204,
    dependencies=[Depends(require_role("ADMIN", "COORDINATOR"))]
)
def delete_grade(
    grade_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    g = db.get(SchoolGrade, grade_id)
    if not g:
        raise HTTPException(status_code=404, detail="Série não encontrada")

    db.delete(g); db.commit()
    return None
