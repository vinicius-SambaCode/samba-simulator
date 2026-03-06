from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Session

from app.models.models import User, Role
from app.core.security import hash_password
from app.core.db import SessionLocal


def get_or_create_role(db: Session, name: str) -> Role:
    role = db.query(Role).filter(Role.name == name).first()

    if not role:
        role = Role(name=name)
        db.add(role)
        db.commit()
        db.refresh(role)

    return role


def seed_roles(db: Session):
    roles = [
        "admin",
        "teacher",
        "student",
        "COORDINATOR",
    ]

    for r in roles:
        get_or_create_role(db, r)


def seed_admin(db: Session):
    email = "admin@samba.local"

    user = db.query(User).filter(User.email == email).first()

    if user:
        print("✔ Admin já existe")
        return

    print("👤 Criando usuário admin...")

    user = User(
        name="Administrador",
        email=email,
        password_hash=hash_password("admin123"),
        is_active=True,
        created_at=datetime.utcnow(),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    admin_role = get_or_create_role(db, "admin")
    coord_role = get_or_create_role(db, "COORDINATOR")

    user.roles.append(admin_role)
    user.roles.append(coord_role)

    db.commit()

    print("✅ Admin criado")


def run_seed(db: Session):
    seed_roles(db)
    seed_admin(db)


def main():
    db = SessionLocal()

    try:
        run_seed(db)
        print("🌱 Seed executado com sucesso")
    finally:
        db.close()


if __name__ == "__main__":
    main()
