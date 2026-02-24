"""
=========================================================
ROTAS - DISCIPLINE
=========================================================

Regras:
- ADMIN e COORDINATOR podem criar
- Todos autenticados podem listar
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.core.permissions import require_role
from app.core.security import get_current_user
from app.models.base_models import Discipline
from app.schemas.discipline import DisciplineCreate, DisciplineOut


router = APIRouter(prefix="/disciplines", tags=["disciplines"])


# ==========================================================
# LISTAR DISCIPLINAS
# ==========================================================

@router.get("/", response_model=List[DisciplineOut])
def list_disciplines(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Discipline).all()


# ==========================================================
# CRIAR DISCIPLINA
# ==========================================================

@router.post(
    "/",
    response_model=DisciplineOut,
    dependencies=[Depends(require_role("ADMIN", "COORDINATOR"))]
)
def create_discipline(
    data: DisciplineCreate,
    db: Session = Depends(get_db)
):
    exists = db.query(Discipline).filter(Discipline.name == data.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Disciplina já existe")

    discipline = Discipline(name=data.name)

    db.add(discipline)
    db.commit()
    db.refresh(discipline)

    return discipline