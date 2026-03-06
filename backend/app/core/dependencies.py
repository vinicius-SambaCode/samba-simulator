# =============================================================================
# app/core/dependencies.py
# =============================================================================
#
# SHIM DE COMPATIBILIDADE — NÃO ADICIONE LÓGICA AQUI.
#
# Este arquivo existe somente para não quebrar imports antigos enquanto
# a base de código migra gradualmente para app.core.deps.
#
# ANTES (como as rotas importavam):
#   from app.core.dependencies import require_role   ← funcionava
#
# AGORA (como as rotas devem importar):
#   from app.core.deps import require_role           ← canônico
#
# Ambas as formas funcionam durante a migração.
# Quando todos os arquivos estiverem usando app.core.deps,
# este shim pode ser removido com segurança.
# =============================================================================

# Reexporta tudo de deps.py — ponto canônico de verdade
from app.core.deps import get_current_user, require_role  # noqa: F401

__all__ = ["get_current_user", "require_role"]