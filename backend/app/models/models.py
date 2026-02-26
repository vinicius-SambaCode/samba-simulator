"""
===============================================================================
MODELS AGREGADOR
===============================================================================

Este arquivo NÃO define modelos.

Ele apenas centraliza imports dos modelos ORM para que o Alembic
e outras partes do sistema possam importar tudo de um único lugar.

IMPORTANTE:
NUNCA redefinir tabelas aqui.
Todas as entidades principais vivem em base_models.py.

===============================================================================
"""

# =============================================================================
# IMPORTAÇÃO DO NÚCLEO DO SISTEMA
# =============================================================================

from app.models.base_models import (
    Base,
    Role,
    User,
    Discipline,
    Skill,
    Item,
    user_roles,
    DifficultyEnum,
    ItemTypeEnum,
)

# =============================================================================
# IMPORTAÇÃO DE MODELOS COMPLEMENTARES
# =============================================================================

from app.models.refresh_token import RefreshToken

# =============================================================================
# EXPORTAÇÃO EXPLÍCITA (boa prática para organização)
# =============================================================================

__all__ = [
    "Base",
    "Role",
    "User",
    "Discipline",
    "Skill",
    "Item",
    "RefreshToken",
    "user_roles",
    "DifficultyEnum",
    "ItemTypeEnum",
]
