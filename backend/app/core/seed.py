from sqlalchemy.orm import Session
from app.models.models import User
from app.models.models import Role
from app.core.security import hash_password
from datetime import datetime


def seed_roles(db: Session):
    roles = ["admin", "teacher", "student"]

    for role_name in roles:
        exists = db.query(Role).filter(Role.name == role_name).first()
        if not exists:
            db.add(Role(name=role_name))

    db.commit()


def seed_admin(db: Session):
    admin_email = "admin@samba.local"

    admin = db.query(User).filter(User.email == admin_email).first()
    if admin:
        return

    new_admin = User(
        name="Administrador",
        email=admin_email,
        password_hash=hash_password("admin123"),
        is_active=True,
        created_at=datetime.utcnow()
    )

    db.add(new_admin)
    db.commit()


def run_seed(db: Session):
    seed_roles(db)
    seed_admin(db)
