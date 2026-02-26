"""
=========================================================
MAIN APPLICATION ENTRYPOINT
=========================================================
"""

from fastapi import FastAPI
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.core.seed import run_seed

# Routers
from app.routes.auth import router as auth_router
from app.routes.discipline import router as discipline_router

from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.core.seed import run_seed
# ==========================================================
# APP INIT
# ==========================================================

app = FastAPI(title="SAMBA Simulator API")


# ==========================================================
# STARTUP EVENT
# ==========================================================

# =============================================================================
# STARTUP EVENT - SEED AUTOMÁTICO
# =============================================================================

@app.on_event("startup")
def startup_event():
    """
    Executa seed automático ao iniciar a aplicação.
    Cria roles padrão e admin inicial.
    """
    db: Session = SessionLocal()
    try:
        run_seed(db)
        print("🌱 Seed verificado/executado com sucesso.")
    finally:
        db.close()


# ==========================================================
# ROUTES
# ==========================================================

app.include_router(auth_router)
app.include_router(discipline_router)