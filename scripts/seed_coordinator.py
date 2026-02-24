
# scripts/seed_coordinator.py
import os
import sys

# Garante que 'backend' está no PYTHONPATH para permitir imports 'from app...'
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models.base_models import User, RoleEnum

def run():
    """
    Cria um usuário Coordenador padrão para login nos testes.
    Ajuste o e-mail para um domínio válido (ex.: samba.com, samba.edu, etc).
    """
    db: Session = SessionLocal()
    try:
        email = "coord@samba.com"  # <-- use domínio válido (não use .local)
        name = "Coordenador"
        pwd  = "SenhaForte123"

        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"Coordenador já existe: {email}")
            return

        user = User(
            name=name,
            email=email,
            password_hash=hash_password(pwd),
            role=RoleEnum.coordinator,
            is_active=True
        )
        db.add(user)
        db.commit()
        print(f"Coordenador criado: {email}  |  Senha: {pwd}")
    finally:
        db.close()

if __name__ == "__main__":
    run()
