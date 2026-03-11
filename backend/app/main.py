# =============================================================================
# app/main.py
# =============================================================================
#
# RESPONSABILIDADE DESTE ARQUIVO:
#   - Criar e configurar a instância FastAPI
#   - Registrar middlewares (CORS, Security Headers)
#   - Configurar o Swagger local (sem CDN externo)
#   - Registrar todos os routers do sistema
#
# O QUE MUDOU NO PASSO 3:
#   REMOVIDO o bloco "HEALTH FALLBACK" que estava no final deste arquivo.
#
#   ANTES: havia dois endpoints /health:
#     1. app/routes/health.py  → registrado via _include_router()
#     2. @app.get("/health")   → definido direto aqui (fallback)
#
#   Isso causava o warning nos testes:
#     "Duplicate Operation ID health_health_get for function health"
#
#   AGORA: apenas app/routes/health.py define o /health.
#          O fallback foi removido. Comportamento idêntico, sem warnings.
#
# =============================================================================

from __future__ import annotations
import os as _os

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

from fastapi.staticfiles import StaticFiles


# =============================================================================
# INSTÂNCIA FASTAPI
# =============================================================================
# docs_url, redoc_url e openapi_url são desativados aqui porque servimos
# o Swagger de forma customizada abaixo (usando assets locais, sem CDN).
# Isso é importante para ambientes sem acesso à internet (como a rede escolar).
# =============================================================================

app = FastAPI(
    title="SAMBA Simulator API",
    version="0.1.0",
    docs_url=None,      # Swagger customizado em /docs (abaixo)
    redoc_url=None,     # ReDoc desativado
    openapi_url=None,   # OpenAPI JSON em /_openapi.json (abaixo)
)

print(f"[BOOT] main.py carregado de: {__file__}")


# =============================================================================
# CORS
# =============================================================================
# Lê as origens permitidas da variável de ambiente CORS_ORIGINS.
# Se não definida, permite apenas localhost:3000 (frontend em dev).
#
# Em produção, defina no .env:
#   CORS_ORIGINS=https://seu-frontend.com,https://outro-dominio.com
# =============================================================================

def _normalize_origins(raw: str | None) -> List[str]:
    """Converte string CSV de origens em lista, com fallback para localhost."""
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
    allow_credentials=True,    # necessário para o cabeçalho Authorization
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Authorization"],
)


# =============================================================================
# SECURITY HEADERS
# =============================================================================
# Headers de segurança adicionados a TODAS as respostas.
#
# X-Frame-Options: DENY
#   Impede que a página seja carregada em <iframe> (proteção contra clickjacking)
#
# X-Content-Type-Options: nosniff
#   Impede que o browser "adivinhe" o tipo de conteúdo (proteção contra MIME sniffing)
#
# Referrer-Policy: strict-origin-when-cross-origin
#   Controla quais informações de referência são enviadas em requisições cross-origin
#
# Content-Security-Policy:
#   Em dev: permite conexão com o frontend local (localhost:3000)
#   Em produção: ajuste para o domínio real do frontend
# =============================================================================

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response: Response = await call_next(request)

    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "connect-src 'self' http://localhost:3000 http://127.0.0.1:3000; "
        "img-src 'self' data:; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'; "
    )

    return response


# =============================================================================
# OPENAPI CUSTOMIZADO
# =============================================================================
# Forçamos a versão OpenAPI para 3.0.3 (compatibilidade com swagger-ui-bundle).
# O schema é gerado uma vez e cacheado em memória (_openapi_cache).
# =============================================================================

_openapi_cache: Optional[Dict[str, Any]] = None


def custom_openapi() -> Dict[str, Any]:
    """
    Gera e cacheia o schema OpenAPI do sistema.
    Chamado automaticamente pelo FastAPI quando alguém acessa /_openapi.json.
    """
    global _openapi_cache
    if _openapi_cache:
        return _openapi_cache

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description="API do SAMBA Simulator — Sistema de Avaliação e Monitoramento do Banco de questões para Avaliações",
        routes=app.routes,
    )

    # Força OpenAPI 3.0.3 (swagger-ui-bundle requer esta versão)
    schema["openapi"] = "3.0.3"
    _openapi_cache = schema
    return schema


app.openapi = custom_openapi  # type: ignore


@app.get("/_openapi.json", include_in_schema=False)
def openapi_endpoint():
    """Endpoint que serve o schema OpenAPI em JSON."""
    return JSONResponse(app.openapi())


# =============================================================================
# SWAGGER LOCAL (sem CDN externo)
# =============================================================================
# Os assets do Swagger UI são servidos localmente via StaticFiles.
# Isso garante que o sistema funcione mesmo sem acesso à internet —
# importante para uso em laboratórios de informática de escolas públicas.
# =============================================================================

app.mount(
    "/static/swagger",
    StaticFiles(directory=swagger_ui_3_path),
    name="swagger",
)

_storage_dir = _os.environ.get("STORAGE_DIR", "/app/storage")
if _os.path.isdir(_storage_dir):
    app.mount(
        "/media",
        StaticFiles(directory=_storage_dir),
        name="media",
    )

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Serve o Swagger UI usando assets locais."""
    return get_swagger_ui_html(
        openapi_url="/_openapi.json",
        title="SAMBA Simulator API — Docs",
        swagger_js_url="/static/swagger/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger/swagger-ui.css",
        swagger_favicon_url="/static/swagger/favicon-32x32.png",
    )


@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def swagger_ui_redirect():
    """Redirect OAuth2 exigido pelo fluxo de autorização do Swagger UI."""
    return get_swagger_ui_oauth2_redirect_html()




# =============================================================================
# REGISTRO DE ROUTERS
# =============================================================================
# Os routers são carregados dinamicamente via importlib.
# Vantagem: se um router falhar ao importar, o sistema sobe mesmo assim
# e o erro aparece no log como [WARN], sem derrubar a API toda.
#
# Ordem dos routers (informativa — não afeta o comportamento):
#   auth            → login, refresh, logout, /me, criar usuário
#   discipline      → CRUD de disciplinas
#   grade           → CRUD de séries/anos (SchoolGrade)
#   classes         → CRUD de turmas (SchoolClass, ClassSection)
#   exam            → fluxo completo do simulado
#   students        → CRUD de alunos
#   students_import → importação via CSV (SEDUC-SP)
#   skill           → habilidades BNCC
#   item            → banco de itens
#   blueprint       → matriz de referência do simulado
#   pdf             → geração e download de PDFs
#   health          → /health (monitoramento)
# =============================================================================

def _include_router(module_name: str, var_name: str = "router") -> None:
    """
    Importa e registra um router no app.
    Erros de import são logados como [WARN] e não interrompem a inicialização.
    """
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
    "app.routes.health",   # ← define o /health  (único lugar)
    "app.routes.coordinator_dashboard",
    "app.routes.questions_crud",
    "app.routes.omr",
    "app.routes.notifications",
]

for r in _routers:
    _include_router(r)


# =============================================================================
# NOTA SOBRE O /health
# =============================================================================
# O endpoint /health está definido APENAS em app/routes/health.py.
#
# Não existe mais um @app.get("/health") neste arquivo.
# O fallback foi removido no Passo 3 para eliminar o Operation ID duplicado
# que gerava warning nos testes:
#   "Duplicate Operation ID health_health_get for function health"
# =============================================================================
