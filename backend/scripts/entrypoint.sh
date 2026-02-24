#!/usr/bin/env bash
set -e

echo "🔧 Iniciando SAMBA SIMULATOR Backend..."
echo "DB = $DATABASE_URL"

# Garante diretório de storage
mkdir -p "${STORAGE_DIR:-/app/storage}"

# Aguarda Postgres
/app/scripts/wait-for.sh "${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432}" -- echo "DB OK ✔️"

# Rodar migrations
echo "▶️ Alembic upgrade head..."
alembic upgrade head

# Iniciar API
echo "🚀 Iniciando Uvicorn..."
uvicorn app.main:app --host 0.0.0.0 --port 8000