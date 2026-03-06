"""
===============================================================================
MODELS AGREGADOR
===============================================================================

Este arquivo NÃO define modelos ORM.

Ele funciona como um ponto central de importação para que:

• Alembic detecte todas as tabelas
• FastAPI carregue os modelos corretamente
• Evitemos circular imports

ARQUITETURA:

models/
   base_models.py      → entidades principais do sistema
   refresh_token.py    → modelo de autenticação
   models.py           → agregador (este arquivo)

IMPORTANTE
----------

Nunca definir novas tabelas aqui.

Toda entidade deve ser criada em um arquivo próprio dentro de models/.

===============================================================================
"""

# =============================================================================
# IMPORTAÇÃO DOS MODELOS PRINCIPAIS
# =============================================================================

"""
Esses modelos compõem o núcleo pedagógico do sistema.

Incluem:

• usuários
• papéis
• disciplinas
• habilidades
• banco de itens
"""

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
# MODELOS DE AUTENTICAÇÃO
# =============================================================================

"""
Modelo usado para gerenciamento de refresh tokens
no sistema de autenticação JWT.
"""

from app.models.refresh_token import RefreshToken


# =============================================================================
# EXPORTAÇÃO CONTROLADA
# =============================================================================

"""
__all__ define explicitamente quais objetos podem ser
importados quando alguém fizer:

from app.models.models import *

Isso evita vazamento de símbolos internos.
"""

__all__ = [
    "Base",

    # auth
    "RefreshToken",

    # usuários
    "Role",
    "User",
    "user_roles",

    # currículo
    "Discipline",
    "Skill",

    # banco de itens
    "Item",
    "DifficultyEnum",
    "ItemTypeEnum",
]
