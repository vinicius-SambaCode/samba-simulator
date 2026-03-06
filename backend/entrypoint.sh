#!/usr/bin/env bash
set -e

echo "🚀 Iniciando Samba Simulator API..."

echo "⏳ Aguardando banco de dados..."

python << END
import time
import psycopg2
import os

while True:
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            dbname=os.getenv("POSTGRES_DB"),
        )
        conn.close()
        print("✅ Banco conectado")
        break
    except Exception as e:
        print("⏳ Banco ainda não disponível...")
        time.sleep(2)
END

echo "📦 Rodando migrations..."

alembic upgrade head

echo "🌱 Rodando seed inicial..."

python -m app.core.seed

echo "🚀 Iniciando API..."

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload