# =============================================================================
# app/core/deps.py
# =============================================================================
#
# RESPONSABILIDADE DESTE ARQUIVO:
#   Ponto único de dependências de autorização (RBAC) do sistema.
#
# O QUE MUDOU NO PASSO 2:
#   ANTES: havia dois arquivos com o mesmo propósito:
#     - dependencies.py  (continha a lógica real)
#     - deps.py          (shim que re-exportava de dependencies.py)
#
#   AGORA: deps.py é o arquivo CANÔNICO com toda a lógica.
#          dependencies.py passa a ser o shim (para não quebrar
#          código legado enquanto atualizamos todos os imports).
#
# REGRA: todos os arquivos novos importam de app.core.deps.
#        Nunca criar um terceiro arquivo para o mesmo propósito.
#
# RELAÇÃO COM OUTROS MÓDULOS:
#   app/core/security.py  → fornece get_current_user (autenticação JWT)
#   app/core/deps.py      → fornece require_role (autorização RBAC)
#   app/routes/*.py       → consomem ambos via Depends()
# =============================================================================

from __future__ import annotations

from typing import Set

from fastapi import Depends, HTTPException, status

# Importa a função de autenticação (quem é o usuário)
from app.core.security import get_current_user

# Importa o model ORM do usuário
from app.models.base_models import User


# =============================================================================
# FUNÇÃO INTERNA: coletar nomes dos papéis do usuário
# =============================================================================

def _collect_user_role_names(user: User) -> Set[str]:
    """
    Retorna um conjunto com os nomes de todos os papéis do usuário.

    Suporta dois modelos de armazenamento de papéis:

    MODELO ATUAL (N:N via tabela user_roles):
        user.roles → lista de objetos Role
        Cada Role tem um campo .name (ex.: "ADMIN", "COORDINATOR", "TEACHER")

    MODELO LEGADO (campo único):
        user.role → um único papel (string ou objeto)
        Mantido para compatibilidade com migrations antigas.

    Exemplos de retorno:
        {"COORDINATOR"}
        {"ADMIN", "COORDINATOR"}  ← usuário com dois papéis
    """
    names: Set[str] = set()

    # --- Modelo atual: relação N:N ---
    roles_attr = getattr(user, "roles", None)
    if roles_attr:
        for r in roles_attr:
            name = getattr(r, "name", None)
            if name:
                names.add(name)
            else:
                # caso o papel seja uma string diretamente
                names.add(str(r))

    # --- Fallback legado: campo role único ---
    if not names:
        legacy = getattr(user, "role", None)
        if legacy:
            name = getattr(legacy, "name", None)
            if name:
                names.add(name)
            else:
                names.add(str(legacy))

    return names


# =============================================================================
# DEPENDÊNCIA PÚBLICA: require_role
# =============================================================================

def require_role(*required_roles: str):
    """
    Dependência FastAPI que restringe acesso por papel (RBAC).

    Como usar nas rotas:

    ① Restringir a um único papel:
        @router.post("/simulado")
        def criar_simulado(
            user = Depends(require_role("COORDINATOR"))
        ):

    ② Permitir múltiplos papéis (qualquer um dos dois):
        @router.delete("/questao/{id}")
        def deletar_questao(
            user = Depends(require_role("ADMIN", "COORDINATOR"))
        ):

    ③ Usar como dependência de rota sem injetar o usuário:
        @router.post("/restrito", dependencies=[Depends(require_role("ADMIN"))])
        def rota_restrita():
            ...

    Papéis disponíveis no sistema:
        "ADMIN"       → acesso total (criado pelo seed)
        "COORDINATOR" → abre simulados, acompanha progresso, gera PDFs
        "TEACHER"     → alimenta questões durante o período de coleta

    Comportamento:
        - O acesso é PERMITIDO se o usuário tiver pelo menos UM dos papéis.
        - Se nenhum papel bater: HTTP 403 Forbidden.
        - Se o usuário não estiver autenticado: HTTP 401 (via get_current_user).
    """

    if not required_roles:
        raise ValueError(
            "require_role() precisa de pelo menos um papel. "
            "Exemplo: require_role('ADMIN') ou require_role('ADMIN', 'COORDINATOR')"
        )

    def checker(current_user: User = Depends(get_current_user)) -> User:
        """
        Função interna executada pelo FastAPI a cada requisição.
        Recebe o usuário autenticado e verifica seus papéis.
        """
        user_roles = _collect_user_role_names(current_user)

        # Verifica se há pelo menos um papel em comum
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar este recurso.",
            )

        # Retorna o usuário para que a rota possa usá-lo se quiser
        return current_user

    return checker


# =============================================================================
# REEXPORTAÇÃO: get_current_user
# =============================================================================
# Reexportamos get_current_user aqui para que as rotas possam importar
# ambas as dependências de um único lugar:
#
#   from app.core.deps import get_current_user, require_role
#
# (Opcional — as rotas também podem continuar importando diretamente
#  de app.core.security. As duas formas são equivalentes.)
# =============================================================================

__all__ = [
    "get_current_user",   # reexportado de security.py
    "require_role",       # definido aqui
]
