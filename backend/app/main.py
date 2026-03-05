# app/main.py
from __future__ import annotations

import importlib
import os
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, Response
from fastapi.openapi.utils import get_openapi
from swagger_ui_bundle import swagger_ui_3_path


# ==========================================================
# APP BASE
# ==========================================================
app = FastAPI(
    title="SAMBA Simulator API",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

print(f"[BOOT] main.py carregado de: {__file__}")


# ==========================================================
# CORS — versão correta para frontend separado
# ==========================================================
def _normalize_origins(raw: str | None) -> List[str]:
    if not raw:
        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    return [o.strip() for o in raw.split(",") if o.strip()]


allowed_origins = _normalize_origins(os.getenv("CORS_ORIGINS"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,   # IMPORTANTE se usar Authorization header
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Authorization"],
)


# ==========================================================
# SECURITY HEADERS (sem quebrar integração)
# ==========================================================
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response: Response = await call_next(request)

    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Em dev, permitir conexão com frontend
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "connect-src 'self' http://localhost:3000 http://127.0.0.1:3000; "
        "img-src 'self' data:; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'; "
    )

    return response


# ==========================================================
# OPENAPI CONTROLADO
# ==========================================================
_openapi_cache: Optional[Dict[str, Any]] = None

def custom_openapi() -> Dict[str, Any]:
    global _openapi_cache
    if _openapi_cache:
        return _openapi_cache

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description="API do Samba Simulator",
        routes=app.routes,
    )

    schema["openapi"] = "3.0.3"
    _openapi_cache = schema
    return schema


app.openapi = custom_openapi  # type: ignore


@app.get("/_openapi.json", include_in_schema=False)
def openapi_endpoint():
    return JSONResponse(app.openapi())


# ==========================================================
# SWAGGER LOCAL
# ==========================================================
app.mount("/static/swagger", StaticFiles(directory=swagger_ui_3_path), name="swagger")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/_openapi.json",
        title="SAMBA Simulator API — Docs",
        swagger_js_url="/static/swagger/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger/swagger-ui.css",
        swagger_favicon_url="/static/swagger/favicon-32x32.png",
    )

@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


# ==========================================================
# ROUTERS
# ==========================================================
def _include_router(module_name: str, var_name: str = "router") -> None:
    try:
        mod = importlib.import_module(module_name)
        router = getattr(mod, var_name)
        app.include_router(router)
        print(f"[OK] Router incluído: {module_name}")
    except Exception as e:
        print(f"[WARN] Erro ao incluir router {module_name}: {e}")


_routers = [
    "app.routes.auth",
    "app.routes.discipline",
    "app.routes.grade",
    "app.routes.classes",
    "app.routes.exam",
    "app.routes.students",
    "app.routes.students_import",
    "app.routes.skill",
    "app.routes.item",
    "app.routes.blueprint",
    "app.routes.pdf",
    "app.routes.health",
]

for r in _routers:
    _include_router(r)


# ==========================================================
# HEALTH FALLBACK
# ==========================================================
@app.get("/health")
def health():
    return {"status": "ok"}