
# scripts/test_db_conn.py
import os, sys

PROJ_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
empty_pgpass = os.path.join(PROJ_DIR, "empty_pgpass.conf")
empty_pg_dir = os.path.join(PROJ_DIR, "empty_pg_dir")
os.makedirs(empty_pg_dir, exist_ok=True)
with open(empty_pgpass, "a", encoding="utf-8") as f:
    pass

# BLINDAGEM total do libpq
os.environ["PGPASSFILE"]       = empty_pgpass
os.environ["PGSERVICEFILE"]    = empty_pgpass
os.environ["PGSYSCONFDIR"]     = empty_pg_dir
os.environ["PGCLIENTENCODING"] = "UTF8"
os.environ["PGSERVICE"]        = ""
os.environ["LC_ALL"]           = "C"
os.environ["LANG"]             = "C"

# (Opcional, força o AppData para um diretório controlado)
# os.environ["APPDATA"] = empty_pg_dir

# PYTHONPATH para 'app'
BASE_DIR = os.path.join(PROJ_DIR, "backend")
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

print("DEBUG | PGPASSFILE   =", os.environ.get("PGPASSFILE"))
print("DEBUG | PGSYSCONFDIR =", os.environ.get("PGSYSCONFDIR"))
print("DEBUG | PGSERVICEFILE=", os.environ.get("PGSERVICEFILE"))
print("DEBUG | LC_ALL/LANG  =", os.environ.get("LC_ALL"), os.environ.get("LANG"))

from app.core.settings import settings
print("DATABASE_URL =", settings.DATABASE_URL)

import psycopg2
print("psycopg2 version:", getattr(psycopg2, "__version__", "unknown"))

conn = psycopg2.connect(
    host="127.0.0.1",
    port=5432,
    dbname="samba_simulator",
    user="postgres",
    password="postgres",
)
print("OK: conexão aberta!")
conn.close()
print("OK: conexão fechada!")
