# =============================================================================
# app/core/db.py
# =============================================================================
#
# RESPONSABILIDADE DESTE ARQUIVO:
#   - Criar a engine de conexão com o PostgreSQL
#   - Criar a fábrica de sessões (SessionLocal)
#   - Fornecer a dependência get_db() para injeção nas rotas FastAPI
#
# O QUE MUDOU NO PASSO 1:
#   ANTES: este arquivo criava sua própria Base declarativa:
#            class Base(DeclarativeBase): pass   ← ERRADO (duplicata)
#
#   AGORA: importa a Base de app/models/base_models.py, que é a única
#          Base do sistema. Isso garante que o Alembic enxergue
#          TODOS os models em uma única varrição de metadata.
#
# FLUXO DE DEPENDÊNCIA:
#   alembic/env.py
#       └── importa Base de app/models/base_models.py  ← enxerga tudo
#
#   app/routes/*.py
#       └── Depends(get_db)  ← recebe uma Session pronta
# =============================================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings

# -----------------------------------------------------------------------------
# IMPORTANTE: importamos a Base de base_models.py (não criamos uma nova aqui).
# Isso é necessário para que db.py possa ser importado em qualquer lugar
# sem risco de criar um segundo metadata isolado.
#
# O Alembic importa Base via alembic/env.py — certifique-se de que env.py
# faça:   from app.models.base_models import Base
# -----------------------------------------------------------------------------
from app.models.base_models import Base  # noqa: F401 — reexportado para o Alembic


# =============================================================================
# ENGINE
# =============================================================================
# pool_pre_ping=True: antes de usar uma conexão do pool, o SQLAlchemy
#   executa um "SELECT 1" para verificar se ainda está viva.
#   Isso evita erros silenciosos após períodos de inatividade.
#
# future=True: habilita o modo SQLAlchemy 2.x mesmo usando a API 1.x
#   (compatibilidade com código legado enquanto migramos)
# =============================================================================

engine = create_engine(
    settings.DATABASE_URL,
    future=True,
    pool_pre_ping=True,
)


# =============================================================================
# FÁBRICA DE SESSÕES
# =============================================================================
# autocommit=False → você controla quando commitar (padrão seguro)
# autoflush=False  → o SQLAlchemy não envia SQL ao banco antes do commit
#                    (evita surpresas em lógicas complexas)
# =============================================================================

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,
)


# =============================================================================
# DEPENDÊNCIA FastAPI — get_db()
# =============================================================================
# Uso nas rotas:
#
#   @router.get("/exemplo")
#   def exemplo(db: Session = Depends(get_db)):
#       ...
#
# O bloco try/finally garante que a sessão seja SEMPRE fechada,
# mesmo que a rota lance uma exceção.
# =============================================================================

def get_db():
    """
    Gerador de sessão para injeção de dependência via FastAPI Depends().
    Abre uma sessão, entrega para a rota, fecha ao final (com ou sem erro).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Exportação explícita — facilita imports em outros módulos
__all__ = ["engine", "SessionLocal", "Base", "get_db"]
