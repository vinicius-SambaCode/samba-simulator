
# backend/app/core/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.settings import settings



# Engine do SQLAlchemy (usa a DATABASE_URL do .env)
engine = create_engine(
    settings.DATABASE_URL,
    future=True,
    pool_pre_ping=True,  # ajuda a evitar conexões zumbis
)

# Fábrica de sessões
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,
)

# >>> Base declarativa (é ESSA que o Alembic precisa importar)
class Base(DeclarativeBase):
    pass

# Dependência para FastAPI (quando formos usar)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Opcional: facilitar import externo
__all__ = ["engine", "SessionLocal", "Base", "get_db"]
