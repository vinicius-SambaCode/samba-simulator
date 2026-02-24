# SAMBA Simulator — Backend

API **FastAPI** para gestão de simulados educacionais, com:

- **Autenticação** (JWT + Refresh Token) e **RBAC** (ADMIN / COORDINATOR / TEACHER)
- **Módulo Escolar** (séries/anos, turmas, alunos)
- **Simulados (Sprint 1)**: cotas por disciplina, atribuição de professores por turma/disciplina, coleta de questões, travamento
- **PDF (Sprint 2)**: caderno ABNT + **cartão‑resposta OMR** (A–D/A–E, fiduciais, QR Code)
- **(Sprint 3 – em breve)**: leitura óptica OMR via OpenCV (fiduciais, homografia, bolhas, correção, CSV)

> **Stack**: FastAPI, SQLAlchemy, Alembic, PostgreSQL, ReportLab, Pillow, Docker & Docker Compose.

---

## Sumário

- [Arquitetura e Estrutura](#arquitetura-e-estrutura)
- [Requisitos](#requisitos)
- [Subir com Docker (recomendado)](#subir-com-docker-recomendado)
- [Variáveis de Ambiente (`.env`)](#variáveis-de-ambiente-env)
- [Migrations (Alembic)](#migrations-alembic)
- [Seed de Dados (automático e manual)](#seed-de-dados-automaticamente-e-manual)
- [Uso via Swagger](#uso-via-swagger)
- [Fluxo dos Sprints](#fluxo-dos-sprints)
  - [Sprint 1 — Simulado](#sprint-1--simulado)
  - [Sprint 2 — PDF (caderno/OMR)](#sprint-2--pdf-cadernoomr)
  - [Sprint 3 — OMR (em desenvolvimento)](#sprint-3--omr-em-desenvolvimento)
- [Importar Alunos via CSV](#importar-alunos-via-csv)
- [Geração e Download dos PDFs](#geração-e-download-dos-pdfs)
- [Desenvolvimento Local (sem Docker)](#desenvolvimento-local-sem-docker)
- [Troubleshooting (Docker/Windows)](#troubleshooting-dockerwindows)
- [CI (GitHub Actions)](#ci-github-actions)
- [Makefile (opcional)](#makefile-opcional)
- [Licença](#licença)

---

## Arquitetura e Estrutura

## Requisitos

- **Docker Desktop** (Windows/macOS) — no Windows, com **WSL 2**
- **Docker Compose v2**
- (Opcional) Python 3.12+ para rodar local

> 💡 **Windows**: abra o **Docker Desktop** antes de usar `docker compose`.

---

## Subir com Docker (recomendado)

1) Crie seu `.env` a partir do `.env.sample`:

```bash
cp .env.sample .env

#Importante: mantenha POSTGRES_HOST=db e DATABASE_URL apontando para db:5432 (rede do compose).


#Suba a stack:
docker compose up --build

Swagger: http://localhost:8000/docs
O container api executa alembic upgrade head na partida.

Variáveis de Ambiente (.env)
Exemplo (ajuste ao seu cenário):


        APP_NAME=SAMBA-Simulator
        APP_ENV=development
        APP_HOST=0.0.0.0
        APP_PORT=8000
        APP_RELOAD=false

        # JWT / SECURITY
        SECRET_KEY=troque_por_uma_chave_segura
        REFRESH_TOKEN_PEPPER=troque_este_pepper
        ACCESS_TOKEN_EXPIRE_MINUTES=60
        REFRESH_TOKEN_EXPIRE_DAYS=14

        # DB para Docker
        POSTGRES_USER=postgres
        POSTGRES_PASSWORD=troque_senha
        POSTGRES_DB=samba_simulator
        POSTGRES_HOST=db
        POSTGRES_PORT=5432
        DATABASE_URL=postgresql+psycopg2://postgres:troque_senha@db:5432/samba_simulator

        # CORS
        CORS_ALLOW_ORIGINS=http://localhost:5500,http://127.0.0.1:5500

        # Storage
        STORAGE_DIR=/app/storage
    
⚠️ Nunca versione o .env com credenciais reais — suba apenas o .env.sample.



Migrations (Alembic)
    Autoexecutadas no start do container api.
    Comandos úteis (dentro do container):


            # abrir shell no container
            docker compose exec api bash

            # criar uma migration
            alembic revision --autogenerate -m "mensagem"

            # aplicar
            alembic upgrade head


##Seed de Dados (automaticamente e manual)

#Seed automático (opcional, recomendado)


# app/startup_seed.py
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from app.models.base_models import User, Role

ROLES = ["ADMIN", "COORDINATOR", "TEACHER"]
ADMIN_EMAIL = "admin@samba.com"
ADMIN_PASS  = "Admin@123"  # troque em produção

def run(db: Session):
    # garante papéis
    role_objs = {}
    for name in ROLES:
        r = db.query(Role).filter(Role.name == name).first()
        if not r:
            r = Role(name=name); db.add(r); db.flush()
        role_objs[name] = r

    # garante admin
    u = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if not u:
        u = User(
            email=ADMIN_EMAIL,
            name="Administrador",
            password_hash=bcrypt.hash(ADMIN_PASS),
            is_active=True,
        )
        db.add(u); db.flush()

    # vincula ADMIN + COORDINATOR
    for rn in ("ADMIN", "COORDINATOR"):
        if role_objs[rn] not in u.roles:
            u.roles.append(role_objs[rn])

#app/main.py:
from fastapi import FastAPI
from app.core.db import SessionLocal
from app.startup_seed import run as run_seed

app = FastAPI(...)

@app.on_event("startup")
def ensure_seed():
    db = SessionLocal()
    try:
        run_seed(db)
        db.commit()
    finally:
        db.close()

#Assim, quando o banco estiver vazio (ex.: após docker compose down -v), os papéis e o admin padrão são recriados automaticamente.

#Seed manual (alternativa)

docker compose exec api bash
python - << 'PY'
from app.core.db import SessionLocal
from app.models.base_models import User, Role
from passlib.hash import bcrypt

db = SessionLocal()

def role(n):
    r = db.query(Role).filter(Role.name==n).first()
    if not r:
        r = Role(name=n); db.add(r); db.flush()
    return r

admin, coord = role("ADMIN"), role("COORDINATOR")

email="admin@samba.com"; pwd="Admin@123"
u = db.query(User).filter(User.email==email).first()
if not u:
    u = User(email=email, name="Administrador",
             password_hash=bcrypt.hash(pwd), is_active=True)
    db.add(u); db.flush()

if admin not in u.roles: u.roles.append(admin)
if coord not in u.roles: u.roles.append(coord)

db.commit()
print("seed OK")
PY

#------------------------------------------------------------------------------------------
'''
Uso via Swagger

Acesse http://localhost:8000/docs
Faça POST /auth/login (username=email, password)
Clique em Authorize e cole Bearer <access_token> para usar as rotas protegidas

'''
Fluxo dos Sprints

Sprint 1 — Simulado

School
    POST /school/grades (séries/anos)
    POST /school/sections (turmas/letras)
    POST /school/classes (combina grade + seção)

Disciplinas / Usuários
    POST /disciplines (Física, Química, Biologia, …)
    POST /auth/users (professores) + atribuir TEACHER

Vínculo institucional (professor ↔ classe ↔ disciplina)
    Usar CRUD que você criou ou inserts na teacher_class_subject.

Exame
    POST /exams (definir options_count: 4|5, answer_source)
    POST /exams/{id}/assign-classes
    POST /exams/{id}/quotas (cotas por disciplina)
    POST /exams/{id}/assign-teachers (valida contra teacher_class_subject)
    Professores: /exams/{id}/questions e /exams/{id}/questions/paste
    Coordenador: /exams/{id}/progress
    Coordenador: /exams/{id}/lock

Sprint 2 — PDF (caderno/OMR)

Geração
    POST /pdf/exams/{id}/pdf/generate?student_id=<id>
    POST /pdf/exams/{id}/pdf/generate?class_id=<id>

Download
    GET /pdf/exams/{id}/pdf/download?type=booklet&student_id=<id>
    GET /pdf/exams/{id}/pdf/download?type=answer_sheet&student_id=<id>

#O cartão OMR inclui fiduciais, QR Code (exam_id|student_id|version) e bolhas A–D/A–E, com coordenadas fixas (compatíveis com a leitura do Sprint 3).

Sprint 3 — OMR (em desenvolvimento)
    Upload de imagens/PDF/ZIP
    Detecção de fiduciais → homografia
    Leitura de QR → identifica student_id / exam_id
    Leitura das bolhas → respostas
    Comparação com gabarito → nota
    Export CSV por exame/turma

#Endpoints propostos:
    POST /omr/upload, GET /omr/result, GET /omr/export/csv, (opcional) POST /omr/answer-key/upload.

##Importar Alunos via CSV
        Endpoint: POST /school/students/import
        Query: class_id ou class_name (ex.: 3ªD)

    Parâmetros:

        dry_run (default true — simulação)
        combine_check_digit (concatena RA + Dig. RA, preservando X)
        Importa apenas “Ativo”

    Comportamento: upsert por RA (atualiza nome/turma se já existir)


#Geração e Download dos PDFs
Gerar (por aluno/turma):
    POST /pdf/exams/{id}/pdf/generate?student_id=...
    POST /pdf/exams/{id}/pdf/generate?class_id=...

Baixar (unitário):
    GET /pdf/exams/{id}/pdf/download?type=booklet|answer_sheet&student_id=...

Arquivos em: storage/exams/{exam_id}/.

        🖨️ Impressão do OMR: escale 100% (sem ajustar à página).

#Desenvolvimento Local (sem Docker)

    Recomendado usar Docker. Caso rode local:

    1 Crie e ative virtualenv (Python 3.12+)
    2 pip install -r requirements.txt
    3 Defina .env apontando para Postgres local (127.0.0.1:5432)
    4 alembic upgrade head
    5 uvicorn app.main:app --reload

#Troubleshooting (Docker/Windows)
Compose procura .env no diretório do docker-compose.yml
→ Rode docker compose up dentro de backend/.


Docker Desktop fechado
→ Erro da pipe dockerDesktopLinuxEngine. Abra o Docker Desktop.


/scripts/wait-for.sh: No such file or directory
→ Corrija no entrypoint.sh o caminho para /app/scripts/wait-for.sh, ou crie um link no Dockerfile:

        RUN ln -s /app/scripts /scripts

CRLF/LF em scripts .sh (Windows)
→ Use LF (VS Code → canto inferior direito → “LF”).


Warning do Compose: the attribute version is obsolete
→ Remova version: "3.9" do docker-compose.yml.


Aviso ruidoso do bcrypt/passlib
→ Use passlib[bcrypt]==1.7.4 com bcrypt==3.2.2 no requirements.txt (rebuild com --no-cache), ou silencie o logger no main.py:

        import logging
        logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)

Resetar banco
→ docker compose down -v apaga volumes (perde dados).
→ Para não perder, use apenas docker compose down ou stop.

##CI (GitHub Actions)
#Crie backend/.github/workflows/ci.yml:
name: CI

on:
  push:
    paths: ['backend/**']
  pull_request:
    paths: ['backend/**']

jobs:
  backend-ci:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install flake8
      - name: Lint
        run: flake8 app --max-line-length=120
      - name: Alembic models import check
        run: |
          python - << 'PY'
          import importlib
          importlib.import_module('app.models.exam')
          importlib.import_module('app.models.school')
          importlib.import_module('app.models.refresh_token')
          print("Models import OK")
          PY
          

   # Em próximo passo, podemos incluir testes e build da imagem Docker no CI.


Makefile (opcional)
backend/Makefile:

up:
    docker compose up --build

down:
    docker compose down

downv:
    docker compose down -v

logs:
    docker compose logs -f api

sh:
    docker compose exec api bash

mig:
    docker compose exec api alembic revision --autogenerate -m "$(m)"

upg:
    docker compose exec api alembic upgrade head

#Uso:

        1 make up      # sobe a stack
        2 make sh      # shell no container
        3 make mig m="ajuste X"
        4 make upg     # upgrade head

Licença
Escolha uma licença (ex.: MIT) e adicione o arquivo LICENSE na raiz do repositório.