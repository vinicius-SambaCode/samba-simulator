from app.core.db import SessionLocal
from app.models.base_models import Role

ROLES_PADRAO = [
    "ADMIN",
    "COORDINATOR",
    "TEACHER",
]

def run():
    db = SessionLocal()

    for role_name in ROLES_PADRAO:
        existing = db.query(Role).filter(Role.name == role_name).first()
        if not existing:
            db.add(Role(name=role_name))

    db.commit()
    db.close()
    print("✔ Roles criadas com sucesso!")

if __name__ == "__main__":
    run()