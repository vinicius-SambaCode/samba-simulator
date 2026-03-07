# -*- coding: utf-8 -*-
"""
app/core/seed.py — Passo 10: Seed expandido
=============================================

Popula o banco com dados realistas para testar o fluxo completo do simulado:

  Estrutura escolar
  -----------------
  Séries (SchoolGrade):
    - Ensino Médio: 1ª, 2ª, 3ª

  Turmas (ClassSection + SchoolClass):
    - Seções: A, B, C
    - Resultado: 3ª A, 3ª B, 3ª C  (foco no 3º ano para testes)
    - Também cria 1ª A e 2ª A para cobertura

  Disciplinas (Discipline):
    - Matemática, Português, Física, Química, Biologia,
      História, Geografia, Inglês

  Usuários
  --------
  - admin@samba.local          (roles: admin, COORDINATOR)  ← já existente
  - coord@samba.local          (role: COORDINATOR)          ← novo
  - prof.matematica@samba.local (role: teacher)
  - prof.portugues@samba.local  (role: teacher)
  - prof.fisica@samba.local     (role: teacher)
  - prof.quimica@samba.local    (role: teacher)

  Mapeamentos (TeacherClassSubject)
  ----------------------------------
  prof.matematica → Matemática em 3ªA, 3ªB, 3ªC
  prof.portugues  → Português  em 3ªA, 3ªB, 3ªC
  prof.fisica     → Física     em 3ªA, 3ªB
  prof.quimica    → Química    em 3ªA, 3ªB

  Resultado
  ---------
  Após o seed você pode:
  1. Criar simulado como admin/coord
  2. assign-classes com IDs das turmas 3ªA, 3ªB, 3ªC
  3. set-quotas para Matemática=5, Português=5
  4. assign-teachers com os professores acima
  5. Inserir questões como prof.matematica
  6. Ver dashboard como coord

  IDEMPOTÊNCIA
  ------------
  Todas as funções são idempotentes — rodar seed duas vezes não duplica dados.
"""

from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Session

from app.models.base_models import User, Role
from app.models.models import Discipline
from app.models.school import EducationLevel, SchoolGrade, ClassSection, SchoolClass
from app.models.exam import TeacherClassSubject
from app.core.security import hash_password
from app.core.db import SessionLocal


# =============================================================================
# Helpers genéricos
# =============================================================================

def _get_or_create_role(db: Session, name: str) -> Role:
    role = db.query(Role).filter(Role.name == name).first()
    if not role:
        role = Role(name=name)
        db.add(role)
        db.flush()
    return role


def _get_or_create_user(
    db: Session,
    name: str,
    email: str,
    password: str,
    role_names: list[str],
) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            is_active=True,
            created_at=datetime.utcnow(),
        )
        db.add(user)
        db.flush()
        print(f"  👤 Criado: {email}")
    else:
        print(f"  ✔  Já existe: {email}")

    existing_roles = {r.name for r in user.roles}
    for rname in role_names:
        if rname not in existing_roles:
            role = _get_or_create_role(db, rname)
            user.roles.append(role)

    return user


def _get_or_create_discipline(db: Session, name: str) -> Discipline:
    disc = db.query(Discipline).filter(Discipline.name == name).first()
    if not disc:
        disc = Discipline(name=name)
        db.add(disc)
        db.flush()
        print(f"  📚 Disciplina: {name}")
    return disc


def _get_or_create_grade(
    db: Session,
    level: EducationLevel,
    year_number: int,
    label: str,
) -> SchoolGrade:
    grade = db.query(SchoolGrade).filter_by(level=level, year_number=year_number).first()
    if not grade:
        grade = SchoolGrade(level=level, year_number=year_number, label=label)
        db.add(grade)
        db.flush()
        print(f"  🏫 Série: {label} ({level})")
    return grade


def _get_or_create_section(db: Session, label: str) -> ClassSection:
    section = db.query(ClassSection).filter_by(label=label).first()
    if not section:
        section = ClassSection(label=label)
        db.add(section)
        db.flush()
    return section


def _get_or_create_class(
    db: Session,
    grade: SchoolGrade,
    section: ClassSection,
    name: str,
) -> SchoolClass:
    sc = db.query(SchoolClass).filter_by(grade_id=grade.id, section_id=section.id).first()
    if not sc:
        sc = SchoolClass(grade_id=grade.id, section_id=section.id, name=name)
        db.add(sc)
        db.flush()
        print(f"  🏷  Turma: {name}")
    return sc


def _get_or_create_teacher_class_subject(
    db: Session,
    teacher: User,
    school_class: SchoolClass,
    discipline: Discipline,
) -> None:
    exists = db.query(TeacherClassSubject).filter_by(
        teacher_user_id=teacher.id,
        class_id=school_class.id,
        discipline_id=discipline.id,
    ).first()
    if not exists:
        db.add(TeacherClassSubject(
            teacher_user_id=teacher.id,
            class_id=school_class.id,
            discipline_id=discipline.id,
        ))


# =============================================================================
# Funções de seed por domínio
# =============================================================================

def seed_roles(db: Session) -> None:
    print("\n📌 Roles...")
    for name in ["admin", "TEACHER", "student", "COORDINATOR"]:
        _get_or_create_role(db, name)


def seed_users(db: Session) -> dict[str, User]:
    print("\n👥 Usuários...")
    users = {}

    users["admin"] = _get_or_create_user(
        db, "Administrador", "admin@samba.local", "admin123",
        ["admin", "COORDINATOR"],
    )
    users["coord"] = _get_or_create_user(
        db, "Coordenadora Pedagógica", "coord@samba.local", "coord123",
        ["COORDINATOR"],
    )
    users["mat"] = _get_or_create_user(
        db, "Prof. Matemática", "prof.matematica@samba.local", "prof123",
        ["TEACHER"],
    )
    users["port"] = _get_or_create_user(
        db, "Prof. Português", "prof.portugues@samba.local", "prof123",
        ["TEACHER"],
    )
    users["fis"] = _get_or_create_user(
        db, "Prof. Física", "prof.fisica@samba.local", "prof123",
        ["TEACHER"],
    )
    users["qui"] = _get_or_create_user(
        db, "Prof. Química", "prof.quimica@samba.local", "prof123",
        ["TEACHER"],
    )

    return users


def seed_disciplines(db: Session) -> dict[str, Discipline]:
    print("\n📚 Disciplinas...")
    names = [
        "Matemática", "Português", "Física", "Química",
        "Biologia", "História", "Geografia", "Inglês",
    ]
    return {n: _get_or_create_discipline(db, n) for n in names}


def seed_school_structure(db: Session) -> dict[str, SchoolClass]:
    print("\n🏫 Estrutura escolar...")

    # Séries do Ensino Médio
    g1 = _get_or_create_grade(db, EducationLevel.MEDIO, 1, "1ª")
    g2 = _get_or_create_grade(db, EducationLevel.MEDIO, 2, "2ª")
    g3 = _get_or_create_grade(db, EducationLevel.MEDIO, 3, "3ª")

    # Seções
    sec_a = _get_or_create_section(db, "A")
    sec_b = _get_or_create_section(db, "B")
    sec_c = _get_or_create_section(db, "C")

    # Turmas
    classes = {}
    classes["1A"] = _get_or_create_class(db, g1, sec_a, "1ªA")
    classes["2A"] = _get_or_create_class(db, g2, sec_a, "2ªA")
    classes["3A"] = _get_or_create_class(db, g3, sec_a, "3ªA")
    classes["3B"] = _get_or_create_class(db, g3, sec_b, "3ªB")
    classes["3C"] = _get_or_create_class(db, g3, sec_c, "3ªC")

    return classes


def seed_teacher_assignments(
    db: Session,
    users: dict[str, User],
    classes: dict[str, SchoolClass],
    disciplines: dict[str, Discipline],
) -> None:
    print("\n🔗 Mapeamentos professor → disciplina → turma...")

    mat  = disciplines["Matemática"]
    port = disciplines["Português"]
    fis  = disciplines["Física"]
    qui  = disciplines["Química"]

    # Matemática: prof.mat nas turmas 3A, 3B, 3C
    for cls_key in ("3A", "3B", "3C"):
        _get_or_create_teacher_class_subject(db, users["mat"], classes[cls_key], mat)

    # Português: prof.port nas turmas 3A, 3B, 3C
    for cls_key in ("3A", "3B", "3C"):
        _get_or_create_teacher_class_subject(db, users["port"], classes[cls_key], port)

    # Física: prof.fis nas turmas 3A, 3B
    for cls_key in ("3A", "3B"):
        _get_or_create_teacher_class_subject(db, users["fis"], classes[cls_key], fis)

    # Química: prof.qui nas turmas 3A, 3B
    for cls_key in ("3A", "3B"):
        _get_or_create_teacher_class_subject(db, users["qui"], classes[cls_key], qui)

    print("  ✔  Mapeamentos criados")


# =============================================================================
# Entry points
# =============================================================================

def run_seed(db: Session) -> None:
    print("🌱 Iniciando seed expandido (Passo 10)...")

    seed_roles(db)
    users = seed_users(db)
    disciplines = seed_disciplines(db)
    classes = seed_school_structure(db)
    seed_teacher_assignments(db, users, classes, disciplines)

    db.commit()

    print("\n✅ Seed concluído!")
    print("\n📋 Resumo para testes:")
    print("  Login coord:       coord@samba.local / coord123")
    print("  Login mat:         prof.matematica@samba.local / prof123")
    print("  Login port:        prof.portugues@samba.local / prof123")

    # Mostra IDs para facilitar o uso no Swagger
    for key, cls in classes.items():
        print(f"  Turma {cls.name}: id={cls.id}")
    for name, disc in disciplines.items():
        d = db.query(Discipline).filter_by(name=name).first()
        if d:
            print(f"  Disciplina {name}: id={d.id}")
    for key, u in users.items():
        print(f"  User {u.email}: id={u.id}")


def main() -> None:
    db = SessionLocal()
    try:
        run_seed(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
