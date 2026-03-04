# app/main.py
from __future__ import annotations  # <-- precisa estar no topo (ou após o docstring)

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

# --- cria app ---
app = FastAPI(
    title="SAMBA Simulator API",
    version="0.1.0",
)

# --- CORS (antes de incluir routers) ---
def _normalize_origins(raw: str | None) -> list[str]:
    if not raw:
        return ["http://localhost:3000", "http://127.0.0.1:3000"]
    items = [o.strip() for o in raw.split(",") if o.strip()]
    return items or ["http://localhost:3000", "http://127.0.0.1:3000"]

allowed_origins = _normalize_origins(os.getenv("CORS_ORIGINS"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,   # ex.: http://localhost:3000, http://127.0.0.1:3000
    allow_credentials=False,         # deixe False enquanto usa Bearer no header (sem cookies)
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=600,
)

# --- Security headers / CSP ---
DOC_PATH_PREFIXES = ("/docs", "/redoc", "/openapi.json")
@app.middleware("http")
async def security_headers(request: Request, call_next):
    resp: Response = await call_next(request)
    # cabeçalhos base
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    app_env = os.getenv("APP_ENV", "production")
    if request.url.path.startswith(DOC_PATH_PREFIXES) and app_env == "development":
        # CSP permissivo o suficiente só para Swagger/Redoc em DEV
        resp.headers["Content-Security-Policy"] = (
            "default-src 'self' data: blob'; "
            "img-src 'self' data:; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' blob:; "
            "font-src 'self' data:; "
        )
    else:
        # CSP estrito para o restante
        resp.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none';"

    return resp

# --- Routers ---
from app.routes.discipline import router as discipline_router  # ajuste nome/caminho conforme seu projeto
app.include_router(discipline_router)

# Se você já criou Grades:
# from app.routes.grade import router as grade_router
# app.include_router(grade_router)

# Se tiver PDF:
# from app.routes.pdf import router as pdf_router
# app.include_router(pdf_router)

# --- Healthcheck ---
@app.get("/healthz")
def healthz():
    return {"status": "ok"}
