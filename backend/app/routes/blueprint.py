"""
=========================================================
ROTAS DE BLUEPRINT
=========================================================

Este módulo controla operações relacionadas a Blueprints.

Controle de acesso:
- LISTAR → usuário autenticado
- CRIAR / EDITAR / EXCLUIR → apenas COORDINATOR

Sistema:
- Autenticação via JWT (get_current_user)
- Autorização via RBAC N:N (require_role)
"""

# ==========================================================
# IMPORTS
# ==========================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

# Banco de dados
from app.core.db import get_db

# Autenticação
from app.core.security import get_current_user

# Autorização (novo sistema)
from app.core.permissions import require_role

# Models
from app.models.base_models import Blueprint, User

# Schemas
from app.schemas.blueprint import BlueprintIn, BlueprintOut


# ==========================================================
# ROUTER
# ==========================================================

router = APIRouter(prefix="/blueprints", tags=["blueprints"])


# ==========================================================
# LISTAR BLUEPRINTS
# ==========================================================

@router.get("/", response_model=list[BlueprintOut])
def list_blueprints(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Lista todos os blueprints cadastrados.

    Qualquer usuário autenticado pode visualizar.
    """

    stmt = select(Blueprint).order_by(Blueprint.id.asc())
    result = db.execute(stmt)

    return result.scalars().all()


# ==========================================================
# CRIAR BLUEPRINT
# ==========================================================

@router.post(
    "/",
    response_model=BlueprintOut,
    status_code=status.HTTP_201_CREATED,
)
def create_blueprint(
    data: BlueprintIn,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("COORDINATOR")),
):
    """
    Cria novo blueprint.

    Apenas COORDINATOR pode criar.
    """

    blueprint = Blueprint(
        name=data.name.strip(),
        description=data.description.strip() if data.description else None,
    )

    db.add(blueprint)
    db.commit()
    db.refresh(blueprint)

    return blueprint


# ==========================================================
# ATUALIZAR BLUEPRINT
# ==========================================================

@router.put("/{blueprint_id}", response_model=BlueprintOut)
def update_blueprint(
    blueprint_id: int,
    data: BlueprintIn,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("COORDINATOR")),
):
    """
    Atualiza blueprint existente.

    Apenas COORDINATOR pode editar.
    """

    blueprint = db.get(Blueprint, blueprint_id)

    if not blueprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blueprint não encontrado",
        )

    blueprint.name = data.name.strip()
    blueprint.description = data.description.strip() if data.description else None

    db.commit()
    db.refresh(blueprint)

    return blueprint


# ==========================================================
# DELETAR BLUEPRINT
# ==========================================================

@router.delete("/{blueprint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blueprint(
    blueprint_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("COORDINATOR")),
):
    """
    Remove blueprint do sistema.

    Apenas COORDINATOR pode excluir.
    """

    blueprint = db.get(Blueprint, blueprint_id)

    if not blueprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blueprint não encontrado",
        )

    db.delete(blueprint)
    db.commit()

    return None