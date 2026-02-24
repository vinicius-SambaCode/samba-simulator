"""
Seed inicial do sistema
Cria papéis padrão e usuário root se não existirem.
"""

from app.core.db import SessionLocal
from app.models.base_models import User, Role
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_root_user():
    db = SessionLocal()

    try:
        # =========================
        # Criar roles padrão
        # =========================
        default_roles = ["ADMIN", "COORDINATOR", "TEACHER"]

        for role_name in default_roles:
            existing_role = db.query(Role).filter(Role.name == role_name).first()
            if not existing_role:
                db.add(Role(name=role_name))

        db.commit()

        # =========================
        # Criar usuário root
        # =========================
        root_email = "admin@samba.com"

        existing_user = db.query(User).filter(User.email == root_email).first()

        if not existing_user:
            admin_role = db.query(Role).filter(Role.name == "ADMIN").first()

            hashed_password = pwd_context.hash("admin123")

            root_user = User(
                name="Administrador",
                email=root_email,
                password_hash=hashed_password,
                roles=[admin_role],
            )

            db.add(root_user)
            db.commit()

            print("Usuário root criado com sucesso.")
        else:
            print("Usuário root já existe.")

    finally:
        db.close()