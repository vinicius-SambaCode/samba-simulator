"""
=========================================================
CONTROLE DE PERMISSÕES (RBAC)
=========================================================
"""

from fastapi import Depends, HTTPException, status
from app.core.security import get_current_user


def require_role(*allowed_roles: str):
    """
    Permite múltiplos papéis.

    Exemplo:
    require_role("ADMIN", "COORDINATOR")
    """

    def role_checker(current_user=Depends(get_current_user)):
        user_roles = [role.name for role in current_user.roles]

        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar este recurso."
            )

        return current_user

    return role_checker