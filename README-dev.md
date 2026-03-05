# Samba Simulator — Guia Rápido de Dev

## Requisitos
- Docker + Docker Compose
- Node 20+ (Frontend)
- Python 3.12+ (opcional, se rodar backend fora do Docker)

## 1) Backend
```powershell
# criar .env
Copy-Item backend/.env.sample backend/.env

# subir containers (db + api)
pwsh -File .\tasks.ps1 up

# migrações
pwsh -File .\tasks.ps1 migrate

# testes
pwsh -File .\tasks.ps1 test

# logs
pwsh -File .\tasks.ps1 logs