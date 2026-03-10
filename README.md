# SAMBA Simulator — Backend

> Sistema de Avaliação e Monitoramento de Bimestral Automatizado  
> Backend FastAPI + PostgreSQL para geração e correção de simulados escolares.

---

## 🚀 Funcionalidades

- **Autenticação** JWT com roles (Admin, Coordenador, Professor)
- **Estrutura escolar** — Séries, turmas, alunos, disciplinas
- **Importação de alunos** via CSV padrão SEDUC-SP
- **Upload de questões** via `.docx` com suporte a equações (OMML→LaTeX) e imagens embutidas
- **Gabarito automático** extraído do `.docx` (`gabarito: X`) ou via CRUD
- **Geração de PDFs** personalizados por aluno (caderno ABNT 2 colunas + folha OMR)
- **Folha OMR profissional** com círculos (A–E), barcode e cabeçalho institucional
- **Lotes de impressão** — PDF por sala, OMR por sala, ZIP individual por RA
- **Scanner OMR** — upload de PDF escaneado, leitura de barcode + OpenCV para detecção de bolhas
- **Correção automática** com nota `(10 / total) × acertos`
- **Devolutiva por disciplina** — nota por área de conhecimento
- **Exportação XLSX** por série com ranking, acertos por questão e cores certo/errado
- **PDF devolutiva individual** com cabeçalho institucional, nota em destaque e tabela de questões
- **ZIP de devolutivas** por turma — um PDF por aluno nomeado pelo RA
- **Dashboard do coordenador** com progresso por simulado

---

## 🏗️ Stack

| Camada | Tecnologia |
|--------|-----------|
| API | FastAPI 0.110 + Uvicorn |
| Banco | PostgreSQL 15 + SQLAlchemy 2 + Alembic |
| PDFs | ReportLab 4.1 |
| OMR | OpenCV 4.8 + pyzbar |
| Planilhas | openpyxl 3.1 |
| Containers | Docker + Docker Compose |

---

## ⚡ Início Rápido

### Pré-requisitos
- Docker Desktop
- Python 3.12+ (para scripts locais)

### 1. Clone e configure

```bash
git clone https://github.com/vinicius-SambaCode/samba-simulator.git
cd samba-simulator/backend
cp .env.sample .env
# Edite .env com suas credenciais se necessário
```

### 2. Suba os containers

```bash
docker compose up -d
```

A API estará disponível em `http://localhost:8000`.  
Documentação interativa: `http://localhost:8000/docs`

### 3. Verifique

```bash
curl http://localhost:8000/health
```

---

## 📁 Estrutura do Projeto

```
backend/
├── app/
│   ├── core/           # DB, segurança, settings, dependências
│   ├── models/         # SQLAlchemy models
│   ├── routes/         # Endpoints FastAPI
│   ├── services/       # Lógica de negócio (PDF, OMR, resultados)
│   └── storage/
│       └── assets/     # Logos institucionais e docx de teste
├── alembic/
│   └── versions/       # Migrations do banco
├── tests/              # Testes automatizados
├── test_gerar_pdf.py   # Script de teste de geração de PDFs
├── test_passo14.py     # Script de teste OMR + resultados
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.sample
```

---

## 🔑 Credenciais padrão (seed)

| Usuário | Senha | Role |
|---------|-------|------|
| `admin@samba.local` | `admin123` | ADMIN |
| `coord@samba.local` | `coord123` | COORDINATOR |
| `prof.fisica@samba.local` | `prof123` | TEACHER |

> ⚠️ Altere as senhas em produção via `.env`.

---

## 📋 Endpoints principais

### Autenticação
```
POST /auth/login          — Login (form-data: username, password)
POST /auth/refresh        — Refresh token
```

### Simulados
```
POST /exams/                          — Criar simulado
POST /exams/{id}/questions/upload     — Upload .docx com questões
POST /exams/{id}/lock                 — Travar simulado para geração
GET  /exams/{id}/links                — Consultar gabarito
PATCH /exams/{id}/links/{lid}/answer  — Atualizar gabarito manualmente
```

### PDFs
```
POST /exams/{id}/pdf/generate         — Gerar PDFs (por turma ou aluno)
GET  /exams/{id}/pdf/download         — Download individual
GET  /exams/{id}/pdf/batch            — Lote: booklets | omr | individual (ZIP)
```

### OMR e Resultados
```
POST /exams/{id}/omr/upload                    — Upload PDF escaneado
GET  /exams/{id}/results                       — Resultados (turma ou aluno)
GET  /exams/{id}/results/export                — XLSX por série
GET  /exams/{id}/results/report/{student_id}   — PDF devolutiva individual
GET  /exams/{id}/results/export/reports        — ZIP devolutivas por turma
```

---

## 🧪 Testes

```bash
# Teste de geração de PDFs
docker compose cp test_gerar_pdf.py api:/tmp/test_gerar_pdf.py
docker compose exec api python /tmp/test_gerar_pdf.py

# Teste OMR + resultados
docker compose cp test_passo14.py api:/tmp/test_passo14.py
docker compose exec api python /tmp/test_passo14.py

# Testes unitários
docker compose exec api pytest tests/ -v
```

---

## 📄 Formato do .docx para questões

Cada questão deve seguir o formato:

```
1. Enunciado da questão aqui.
a) Alternativa A
b) Alternativa B
c) Alternativa C
d) Alternativa D
e) Alternativa E
gabarito: c
```

Suporte a:
- Equações Word (OMML) convertidas automaticamente para LaTeX
- Imagens embutidas extraídas e armazenadas por questão

---

## 🗄️ Migrations

```bash
# Rodar migrations pendentes
docker compose exec api alembic upgrade head

# Criar nova migration
docker compose exec api alembic revision --autogenerate -m "descricao"
```

---

## 📜 Licença

Projeto desenvolvido para uso interno escolar.  
EE Prof. Christino Cabral — Bauru/SP — Secretaria de Estado da Educação de São Paulo.