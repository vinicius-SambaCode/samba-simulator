from app.core.db import SessionLocal
from app.core.seed import run_seed


def seed():
    db = SessionLocal()
    try:
        run_seed(db)
        print("✅ Seed executado com sucesso.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
