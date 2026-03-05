# backend/app/routes/discipline.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.permissions import require_role
from app.core.security import get_current_user
from app.models.base_models import Discipline
from app.schemas.discipline import DisciplineCreate, DisciplineOut

router = APIRouter(prefix="/disciplines", tags=["disciplines"])


# -----------------------------
# Helpers
# -----------------------------
def _fetch_or_404(db: Session, discipline_id: int) -> Discipline:
    obj = db.get(Discipline, discipline_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return obj


# -----------------------------
# Listar todas
# -----------------------------
@router.get("/", response_model=List[DisciplineOut])
def list_disciplines(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return db.query(Discipline).all()


# -----------------------------
# Criar
# -----------------------------
@router.post(
    "/",
    response_model=DisciplineOut,
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
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


# -----------------------------
# NOVO: Buscar por ID (resolve 307→405 dos testes)
# - Fornecemos as duas rotas: com e sem "/"
# - A versão com "/" fica fora do schema para não duplicar no Swagger
# -----------------------------
@router.get("/{discipline_id}", response_model=DisciplineOut)
@router.get(
    "/{discipline_id}/",
    response_model=DisciplineOut,
    include_in_schema=False,
)
def get_discipline(
    discipline_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return _fetch_or_404(db, discipline_id)


# -----------------------------
# Atualizar
# -----------------------------
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
    d = _fetch_or_404(db, discipline_id)

    # Impede nome duplicado em outro ID
    exists = (
        db.query(Discipline)
        .filter(Discipline.name == data.name, Discipline.id != discipline_id)
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Já existe disciplina com esse nome")

    d.name = data.name
    db.commit()
    db.refresh(d)
    return d


# -----------------------------
# Deletar
# -----------------------------
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
    d = _fetch_or_404(db, discipline_id)
    db.delete(d)
    db.commit()
    return None
