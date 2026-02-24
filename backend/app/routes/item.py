"""
=========================================================
ROTAS - ITEM
=========================================================
- ADMIN, COORDINATOR e TEACHER podem criar
- Apenas autenticados podem listar
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.core.permissions import require_role
from app.core.security import get_current_user
from app.models.base_models import Item
from app.schemas.item import ItemCreate, ItemOut


router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=List[ItemOut])
def list_items(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Item).all()


@router.post(
    "/",
    response_model=ItemOut,
    dependencies=[Depends(require_role("ADMIN", "COORDINATOR", "TEACHER"))]
)
def create_item(
    data: ItemCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    item = Item(
        owner_id=current_user.id,
        discipline_id=data.discipline_id,
        skill_id=data.skill_id,
        serie=data.serie,
        difficulty=data.difficulty,
        item_type=data.item_type,
        stem=data.stem,
        options_json=data.options_json,
        numeric_answer=data.numeric_answer,
        media_url=data.media_url,
        latex=data.latex
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item