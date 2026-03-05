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
from starlette.responses import Response, JSONResponse
from fastapi.openapi.utils import get_openapi
from swagger_ui_bundle import swagger_ui_3_path


# =====================================================================
# App — desativa docs/redoc padrão (evita CDN) e expõe OpenAPI em rota própria
# =====================================================================
app = FastAPI(
    title="SAMBA Simulator API",
    version="0.1.0",
    docs_url=None,      # sem /docs padrão
    redoc_url=None,     # sem /redoc padrão
    openapi_url=None,   # desliga endpoint automático (vamos expor /_openapi.json)
)

print(f"[BOOT] main.py carregado de: {__file__}")


# =====================================================================
# CORS
# =====================================================================
def _normalize_origins(raw: str | None) -> List[str]:
    if not raw:
        return ["http://localhost:3000", "http://127.0.0.1:3000"]
    items = [o.strip() for o in raw.split(",") if o.strip()]
    return items or ["http://localhost:3000", "http://127.0.0.1:3000"]


allowed_origins = _normalize_origins(os.getenv("CORS_ORIGINS"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,  # manter False enquanto usa Bearer (sem cookies)
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=600,
)


# =====================================================================
# Segurança / CSP
#  - Para /docs, /_openapi.json e /static/swagger/* liberamos o necessário.
#  - Para demais rotas mantemos CSP estrita.
# =====================================================================
DOC_PATH_PREFIXES = ("/docs", "/_openapi.json", "/static/swagger")

@app.middleware("http")
async def security_headers(request: Request, call_next):
    resp: Response = await call_next(request)

    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    app_env = os.getenv("APP_ENV", "production").lower()

    if request.url.path.startswith(DOC_PATH_PREFIXES) and app_env == "development":
        resp.headers["Content-Security-Policy"] = (
            "default-src 'self' data: blob:; "
            "img-src 'self' data:; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' blob:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
        )
    else:
        resp.headers["Content-Security-Policy"] = (
            "default-src 'none'; "
            "frame-ancestors 'none'; "
            "img-src 'self' data:; "
            "style-src 'self'; "
            "script-src 'self'; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
        )
    return resp


# =====================================================================
# OpenAPI — geração controlada (força "3.0.3") + endpoint estável /_openapi.json
# =====================================================================
_openapi_cache: Optional[Dict[str, Any]] = None

def custom_openapi() -> Dict[str, Any]:
    """
    Gera e cacheia o schema OpenAPI **3.0.3** (compatível com Swagger UI local).
    """
    global _openapi_cache
    if _openapi_cache:
        return _openapi_cache

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description="API do Samba Simulator",
        routes=app.routes,
    )
    # Força a versão suportada pelo Swagger UI estável
    schema["openapi"] = "3.0.3"
    _openapi_cache = schema
    return schema

# Override do gerador padrão
app.openapi = custom_openapi  # type: ignore[assignment]

@app.get("/_openapi.json", include_in_schema=False)
def openapi_endpoint() -> JSONResponse:
    return JSONResponse(app.openapi())


# =====================================================================
# Swagger UI 100% local (JS/CSS/Favicon)
# =====================================================================
app.mount("/static/swagger", StaticFiles(directory=swagger_ui_3_path), name="swagger")

FAVICON_PATH = "/static/swagger/favicon-32x32.png"

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/_openapi.json",
        title="SAMBA Simulator API — Docs",
        swagger_js_url="/static/swagger/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger/swagger-ui.css",
        swagger_favicon_url=FAVICON_PATH,
        oauth2_redirect_url="/docs/oauth2-redirect",
    )

@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


# =====================================================================
# Inclusão dos Routers do sistema
#  - Importa e inclui todos os routers conhecidos de app.routes.*
#  - Se algum não existir, apenas loga o aviso (não quebra a app).
# =====================================================================
def _include_router(module_name: str, var_name: str = "router") -> bool:
    try:
        mod = importlib.import_module(module_name)
        router = getattr(mod, var_name, None)
        if router is None:
            print(f"[WARN] Módulo '{module_name}' não possui '{var_name}'.")
            return False
        app.include_router(router)
        print(f"[OK] Router incluído: {module_name}.{var_name}")
        return True
    except Exception as e:
        print(f"[WARN] Falha ao incluir router '{module_name}': {e}")
        return False


# Liste aqui todos os routers que você deseja expor no Swagger
# (com base no conteúdo da pasta app/routes)
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

_health_included = False
for _mod in _routers:
    ok = _include_router(_mod)
    if ok and _mod.endswith(".health"):
        _health_included = True


# =====================================================================
# Health (fallback)
#  - Se não houver router de health, expõe /health básico aqui.
# =====================================================================
if not _health_included:
    @app.get("/health", tags=["health"])
    def health():
        return {"status": "ok"}
