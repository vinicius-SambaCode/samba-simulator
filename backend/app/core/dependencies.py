# -*- coding: utf-8 -*-
"""
Dependências de autorização (RBAC por múltiplos papéis)
------------------------------------------------------
- Reutiliza get_current_user (core/security) como fonte canônica.
- Implementa require_role(*required_roles) para checar papéis.
- Suporta user.roles (N:N) e fallback para legados com user.role único.
"""

from typing import Set
from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user
from app.models.base_models import User


def _collect_user_role_names(user: User) -> Set[str]:
    """
    Extrai os nomes de papéis do usuário:
    - Novo modelo (N:N): user.roles -> roles[i].name
    - Legado: user.role -> role.name OU str(role)
    """
    names: Set[str] = set()

    roles_attr = getattr(user, "roles", None)
    if roles_attr:
        for r in roles_attr:
            name = getattr(r, "name", None)
            names.add(name if name else str(r))

    if not names:
        legacy = getattr(user, "role", None)
        if legacy:
            name = getattr(legacy, "name", None)
            names.add(name if name else str(legacy))

    return names


def require_role(*required_roles: str):
    """
    Exige que o usuário tenha pelo menos UM dos papéis informados.
    Uso:
        Depends(require_role("COORDINATOR"))
        Depends(require_role("COORDINATOR", "ADMIN"))
    """
    if not required_roles:
        raise ValueError("require_role precisa de pelo menos um papel (ex.: 'ADMIN').")

    def checker(current_user: User = Depends(get_current_user)):
        user_roles = _collect_user_role_names(current_user)
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar este recurso.",
            )
        return current_user

    return checker