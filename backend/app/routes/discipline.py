# backend/app/routes/discipline.py  (confira o nome do arquivo!)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.core.permissions import require_role
from app.core.security import get_current_user
from app.models.base_models import Discipline
from app.schemas.discipline import DisciplineCreate, DisciplineOut

router = APIRouter(prefix="/disciplines", tags=["disciplines"])

@router.get("/", response_model=List[DisciplineOut])
def list_disciplines(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return db.query(Discipline).all()

@router.post(
    "/", response_model=DisciplineOut,
    dependencies=[Depends(require_role("ADMIN", "COORDINATOR"))],
)
def create_discipline(
    data: DisciplineCreate,
    db: Session = Depends(get_db),
):
    exists = db.query(Discipline).filter(Discipline.name == data.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Disciplina já existe")
    d = Discipline(name=data.name)
    db.add(d); db.commit(); db.refresh(d)
    return d

# >>> ADICIONE ESTES <<<
@router.put(
    "/{discipline_id}/",  # item COM barra final
    response_model=DisciplineOut,
    dependencies=[Depends(require_role("ADMIN", "COORDINATOR"))],
)
def update_discipline(
    discipline_id: int,
    data: DisciplineCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    d = db.get(Discipline, discipline_id)
    if not d:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")
    exists = (
        db.query(Discipline)
        .filter(Discipline.name == data.name, Discipline.id != discipline_id)
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Já existe disciplina com esse nome")
    d.name = data.name
    db.commit(); db.refresh(d)
    return d

@router.delete(
    "/{discipline_id}/",  # item COM barra final
    status_code=204,
    dependencies=[Depends(require_role("ADMIN", "COORDINATOR"))],
)
def delete_discipline(
    discipline_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    d = db.get(Discipline, discipline_id)
    if not d:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")
    db.delete(d); db.commit()
    return None
