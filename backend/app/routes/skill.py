"""
=========================================================
ROTAS - SKILL
=========================================================
- ADMIN e COORDINATOR podem criar
- Todos autenticados podem listar
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.core.permissions import require_role
from app.core.security import get_current_user
from app.models.base_models import Skill
from app.schemas.skill import SkillCreate, SkillOut


router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/", response_model=List[SkillOut])
def list_skills(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Skill).all()


@router.post(
    "/",
    response_model=SkillOut,
    dependencies=[Depends(require_role("ADMIN", "COORDINATOR"))]
)
def create_skill(
    data: SkillCreate,
    db: Session = Depends(get_db)
):
    exists = db.query(Skill).filter(Skill.code == data.code).first()
    if exists:
        raise HTTPException(status_code=400, detail="Skill já existe")

    skill = Skill(
        code=data.code,
        description=data.description
    )

    db.add(skill)
    db.commit()
    db.refresh(skill)

    return skill