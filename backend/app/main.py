# app/main.py
# -*- coding: utf-8 -*-
"""
MAIN da aplicação
-----------------
Este arquivo registra TODAS as rotas, configura Swagger, CORS e monta a API.
Com este arquivo, todos os novos módulos (auth, disciplinas, school, exams etc.)
vão aparecer corretamente no Swagger.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------
# IMPORTS DOS ROUTERS EXISTENTES
# (ajuste se algum nome for diferente no seu projeto)
# ---------------------------------------
from app.routes.auth import router as auth_router
from app.routes.discipline import router as discipline_router
from app.routes.skill import router as skill_router
from app.routes.item import router as item_router
from app.routes.health import router as health_router

# ---------------------------------------
# IMPORTS DOS NOVOS ROUTERS (SPRINT 1)
# ---------------------------------------
from app.routes.classes import router as school_router        # grades, sections, classes (turmas)
from app.routes.exam import router as exam_router             # simulados (exams, quotas, questões)

# =============================================================================
# INICIALIZAÇÃO DA APLICAÇÃO FASTAPI
# =============================================================================
app = FastAPI(
    title="Samba Simulator API",
    description="""
Sistema de geração de simulados educacionais:
- Gestão escolar (séries/anos, turmas, alunos)
- Gestão de simulados (cotas, questões, gabarito)
- Segurança avançada (JWT + Refresh Token + RBAC)
- Futuro: geração de PDFs ABNT + cartão OMR
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# =============================================================================
# CONFIGURAÇÃO DE CORS
# (Ajuste se no futuro usar domínio fixo)
# =============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Pode trocar por URLs específicas no futuro
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# REGISTRO DOS ROUTERS
# A ordem não importa, mas organizamos por domínio
# =============================================================================

## --- Núcleo / Infra ---
app.include_router(health_router)          # /health

## --- Autenticação ---
app.include_router(auth_router)            # /auth  (login, refresh, logout, users, me)

## --- Disciplinas, Habilidades, Itens ---
app.include_router(discipline_router)      # /disciplines
app.include_router(skill_router)           # /skills
app.include_router(item_router)            # /items

## --- Módulo Escolar (NOVO) ---
app.include_router(school_router)          # /school/grades, /school/sections, /school/classes

## --- Módulo Simulados (NOVO - Sprint 1) ---
app.include_router(exam_router)            # /exams/

## --- Módulo PDF (NOVO - Sprint 2) ---
# Use o formato "módulo + atributo" (menos ruído em linters)
import app.routes.pdf as pdf_routes
app.include_router(pdf_routes.router)      # /pdf/...

## --- Módulo estudante (NOVO - Sprint 2) ---
# Use o formato "módulo + atributo" (menos ruído em linters)
from app.routes.students import router as students_router
app.include_router(students_router)


from app.routes.students_import import router as students_import_router
app.include_router(students_import_router)   # /school/students/import
# =============================================================================
# ROTA RAIZ SIMPLES
# =============================================================================
@app.get("/")
def root():
    return {"detail": "Samba Simulator API is running."}