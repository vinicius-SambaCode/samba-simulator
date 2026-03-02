# app/main.py
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.core.db import SessionLocal
from app.core.seed import run_seed
from app.core.settings import settings

# Routers
from app.routes.auth import router as auth_router
from app.routes.discipline import router as discipline_router
from app.routes.pdf import router as pdf_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ciclo de vida da aplicação:
      - STARTUP: executa o seed de dados mínimos (roles, admin)
      - SHUTDOWN: local para liberar recursos, se necessário
    """
    # STARTUP
    db: Session = SessionLocal()
    try:
      # Tentar sem travar a aplicação caso algo dê errado
      run_seed(db)
      print("🌱 Seed verificado/executado com sucesso.")
    except Exception as e:
      print(f"⚠️ Seed falhou: {e}")
    finally:
      db.close()

    yield

    # SHUTDOWN
    # (adicione aqui se precisar encerrar conexões externas, etc.)


def _normalize_origins(origins_raw: str | None) -> List[str]:
    """
    Lê origens do .env (ex.: 'http://localhost:3000,http://127.0.0.1:3000'),
    normaliza removendo espaços/linhas vazias e aplica fallback seguro
    para ambiente de desenvolvimento.
    """
    if not origins_raw:
        return ["http://localhost:3000", "http://127.0.0.1:3000"]
    items = [o.strip() for o in origins_raw.split(",") if o.strip()]
    return items or ["http://localhost:3000", "http://127.0.0.1:3000"]


# Instância FastAPI com lifespan
app = FastAPI(
    title="SAMBA Simulator API",
    version="1.0.0",
    lifespan=lifespan,
)

# ===== CORS (deve vir antes dos routers) =====
ALLOWED_ORIGINS = _normalize_origins(getattr(settings, "CORS_ORIGINS", None))

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,   # ex.: ["http://localhost:3000"]
    allow_credentials=False,         # use True apenas se usar cookies/credenciais
    allow_methods=["*"],             # ou uma lista específica: ["GET","POST","OPTIONS",...]
    allow_headers=["*"],             # ou lista específica: ["Authorization","Content-Type",...]
    expose_headers=[],               # adicione se precisar expor algum header
    max_age=600,                     # cache do preflight (OPTIONS)
)

# ===== Security headers (após CORS) =====
@app.middleware("http")
async def security_headers(request: Request, call_next):
    resp: Response = await call_next(request)
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # Ajuste o CSP conforme seu front (evite bloquear coisas necessárias)
    resp.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none';"
    # Em produção com HTTPS, você pode ativar HSTS:
    # resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return resp


# ===== Healthcheck =====
@app.get("/healthz", tags=["health"])
def healthz():
    return {"status": "ok"}


# ===== Routers (após middlewares) =====
app.include_router(auth_router)
app.include_router(discipline_router)
app.include_router(pdf_router)
