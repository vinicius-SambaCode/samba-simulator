#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# Samba Simulator API - Entrypoint
# ------------------------------------------------------------------------------
# Metas:
#  - Sair imediatamente em caso de erro (migrations/seed não podem falhar silenciosamente)
#  - Aguardar o banco ficar pronto antes de rodar Alembic
#  - Usar DATABASE_URL como fonte de verdade (fallback em DB_HOST/DB_PORT/POSTGRES_*)
#  - Rodar migrations -> rodar seed -> subir Uvicorn
# ------------------------------------------------------------------------------

# Sair se qualquer comando falhar (-e), se usar variável não setada (-u),
# e falhar se algum comando em pipe falhar (-o pipefail).
# -E garante que ERR trap é herdado em funções/subshells (se fosse usado).
set -Eeuo pipefail

echo "🚀 Iniciando Samba Simulator API..."

# ------------------------------------------------------------------------------
# 1) Resolver parâmetros de conexão ao Postgres
#    Prioridade:
#    (A) DATABASE_URL (postgresql+psycopg2://user:pass@host:port/db)
#    (B) DB_HOST/DB_PORT/POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB
# ------------------------------------------------------------------------------
DATABASE_URL="${DATABASE_URL:-}"

# Função utilitária: imprime uma variável só se existir
_print_var() {
  local key="$1"; local val="${!key:-}"
  if [ -n "${val}" ]; then echo "    - ${key}=${val}"; fi
}

echo "🔧 Variáveis de ambiente relevantes (se definidas):"
_print_var "DATABASE_URL"
_print_var "DB_HOST"
_print_var "DB_PORT"
_print_var "POSTGRES_USER"
_print_var "POSTGRES_PASSWORD"
_print_var "POSTGRES_DB"

# ------------------------------------------------------------------------------
# 2) Aguarda Postgres ficar disponível
#    - Se tiver DATABASE_URL, usa ela (converte para postgresql://)
#    - Senão, usa os campos DB_HOST/DB_PORT/POSTGRES_*
# ------------------------------------------------------------------------------
echo "⏳ Aguardando banco de dados..."

python - <<'PY'
import os
import time
import sys
from urllib.parse import urlparse

# Tenta usar DATABASE_URL (prioridade)
db_url = os.getenv("DATABASE_URL")

def try_connect(host, port, user, password, dbname):
    import psycopg2
    conn = psycopg2.connect(
        host=host, port=int(port or 5432),
        user=user, password=password, dbname=dbname,
        connect_timeout=2
    )
    conn.close()

for attempt in range(1, 61):  # até ~60s de espera
    try:
        if db_url:
            # Alembic/SQLAlchemy geralmente usam "postgresql+psycopg2://"
            # psycopg2 espera "postgresql://"
            url = db_url.replace("postgresql+psycopg2://", "postgresql://", 1)
            u = urlparse(url)
            host = u.hostname or os.getenv("DB_HOST")
            port = u.port or os.getenv("DB_PORT") or 5432
            user = (u.username or os.getenv("POSTGRES_USER"))
            password = (u.password or os.getenv("POSTGRES_PASSWORD"))
            dbname = (u.path.lstrip('/') or os.getenv("POSTGRES_DB"))
            if not all([host, port, user, dbname]):
                raise RuntimeError("DATABASE_URL incompleta. Verifique variáveis.")
            try_connect(host, port, user, password, dbname)
        else:
            # Fallback para variáveis simples
            host = os.getenv("DB_HOST")
            port = os.getenv("DB_PORT", "5432")
            user = os.getenv("POSTGRES_USER")
            password = os.getenv("POSTGRES_PASSWORD")
            dbname = os.getenv("POSTGRES_DB")
            if not all([host, port, user, dbname]):
                raise RuntimeError("Defina DATABASE_URL ou DB_HOST/DB_PORT/POSTGRES_*")
            try_connect(host, port, user, password, dbname)

        print("✅ Banco conectado")
        break
    except Exception as e:
        if attempt >= 60:
            print(f"❌ Banco não respondeu a tempo: {e}", file=sys.stderr)
            sys.exit(1)
        print("⏳ Banco ainda não disponível... (tentativa", attempt, "de 60)")
        time.sleep(1)
PY

# ------------------------------------------------------------------------------
# 3) Alembic migrations (ABORTA se falhar)
# ------------------------------------------------------------------------------
echo "📦 Rodando migrations..."
alembic upgrade head

# ------------------------------------------------------------------------------
# 4) Seed inicial (ABORTA se falhar)
# ------------------------------------------------------------------------------
echo "🌱 Rodando seed inicial..."
python -m app.core.seed

# ------------------------------------------------------------------------------
# 5) Subir API
#    - Use --reload apenas em dev (muda para condicional se quiser)
# ------------------------------------------------------------------------------
echo "🌐 Subindo API..."
# Se você quiser que --reload só ative em dev:
# if [ "${APP_ENV:-development}" = "development" ] || [ "${APP_DEBUG:-false}" = "true" ]; then
#   exec uvicorn app.main:app --host 0.0.0.0 --port "${APP_PORT:-8000}" --reload
# else
#   exec uvicorn app.main:app --host 0.0.0.0 --port "${APP_PORT:-8000}"
# fi
exec uvicorn app.main:app --host 0.0.0.0 --port "${APP_PORT:-8000}" --reload