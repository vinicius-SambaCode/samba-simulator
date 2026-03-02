
# backend/tools/print_conn_info.py
import os
import sys
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.core.settings import settings
from sqlalchemy import create_engine, text

print("URL:", settings.DATABASE_URL)
engine = create_engine(settings.DATABASE_URL, future=True)
with engine.connect() as conn:
    row = conn.execute(text("""
        select current_database(),
               inet_server_addr()::text,
               inet_server_port(),
               current_user,
               current_schema()
    """)).fetchone()
    print("DB:", row[0], "| Host:", row[1], "| Port:", row[2], "| User:", row[3], "| Schema:", row[4])

    exists = conn.execute(text("""
        select exists (
          select 1
          from information_schema.tables
          where table_schema='public' and table_name='disciplines'
        )
    """)).scalar()
    print("disciplines exists:", exists)
