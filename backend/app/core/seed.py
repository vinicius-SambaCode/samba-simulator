from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Session

from app.models.models import User, Role  # ajuste se seus modelos estiverem em outro módulo
from app.core.security import hash_password


def _get_or_create_role(db: Session, role_name: str) -> Role:
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        role = Role(name=role_name)
        db.add(role)
        db.commit()
        db.refresh(role)
    return role


def seed_roles(db: Session) -> None:
    """
    Garante a existência dos papéis básicos.
    Observação:
      - Alguns trechos do seu backend/testes usam "COORDINATOR" (caixa alta).
      - Você já usa "admin/teacher/student" (minúsculos).
    Para evitar dor de cabeça em rotas protegidas, criamos **ambos** quando fizer sentido.
    """
    base_roles = ["admin", "teacher", "student"]
    # Inclua também "COORDINATOR" se suas rotas exigirem esse nome especificamente:
    compat_roles = ["COORDINATOR"]

    for name in base_roles + compat_roles:
        _get_or_create_role(db, name)


def seed_admin(db: Session) -> None:
    """
    Cria o usuário admin padrão (se não existir) e vincula papéis relevantes.
    """
    admin_email = "admin@samba.local"
    admin = db.query(User).filter(User.email == admin_email).first()

    if not admin:
        admin = User(
            name="Administrador",
            email=admin_email,
            password_hash=hash_password("admin123"),
            is_active=True,
            created_at=datetime.utcnow(),
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

    # Vincular papéis (ajuste conforme seu relationship)
    # Se você tem `admin.roles` como relationship:
    needed_roles = ["admin", "COORDINATOR"]
    existing = {r.name for r in getattr(admin, "roles", [])}
    for rname in needed_roles:
        if rname not in existing:
            role = _get_or_create_role(db, rname)
            admin.roles.append(role)  # type: ignore[attr-defined]
    db.commit()


def run_seed(db: Session) -> None:
    seed_roles(db)
    seed_admin(db)
