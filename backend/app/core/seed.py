# -*- coding: utf-8 -*-
"""
app/core/seed.py — Seed de Producao
=====================================
EE Prof. Christino Cabral
  • 1 ROOT + 5 coordenadores + 35 professores reais + 3 usuarios demo
  • 22 turmas com disciplinas exatas conforme matrizes PEI (xlsx)
  • must_change_password=True para usuarios reais (exceto ROOT e demos)
  • Idempotente: rodar novamente nao duplica dados
"""

from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.base_models import User, Role
from app.models.models import Discipline
from app.models.school import EducationLevel, SchoolGrade, ClassSection, SchoolClass
from app.core.security import hash_password
from app.core.db import SessionLocal


# ─────────────────────────────────────────────────────────────────────────────
# 1. USUARIOS
# ─────────────────────────────────────────────────────────────────────────────

USERS_DATA = [
    # (nome, role, email, senha, must_change_password)

    # ROOT
    ("ROOT",                                    "ADMIN",       "root@samba.edvance",              "R7D46S*98/4pwd", False),

    # Coordenadores reais
    ("ALINE CRISTIANE ZORZI",                   "COORDINATOR", "aline_zorzi@samba.edvance",       "Coord@123", True),
    ("CARLA REGINA SPARAPAM DA SILVA",          "COORDINATOR", "carla_silva@samba.edvance",       "Coord@123", True),
    ("FABIO ANGELO AGUIAR",                     "COORDINATOR", "fabio_aguiar@samba.edvance",      "Coord@123", True),
    ("GILCELENE JANAINA RODRIGUES CARDOSO",     "COORDINATOR", "gilcelene_cardoso@samba.edvance", "Coord@123", True),
    ("RAUL DE SOUZA HOFFMANN",                  "COORDINATOR", "raul_hoffmann@samba.edvance",     "Coord@123", True),

    # Professores reais
    ("ADAIANE RODRIGUES MARTINS",               "TEACHER", "adaiane_martins@samba.edvance",   "Prof@123", True),
    ("ANA CAROLINA DE FREITAS NUNES HARTEN",    "TEACHER", "ana_harten@samba.edvance",        "Prof@123", True),
    ("ANA LUCIA MARIANO DOS SANTOS",            "TEACHER", "ana_santos@samba.edvance",        "Prof@123", True),
    ("ANGELICA LONGO DE CAMPOS",                "TEACHER", "angelica_campos@samba.edvance",   "Prof@123", True),
    ("CAMILA CHIQUITO PALHARES",                "TEACHER", "camila_palhares@samba.edvance",   "Prof@123", True),
    ("CESAR AUGUSTO GABURI",                    "TEACHER", "cesar_gaburi@samba.edvance",      "Prof@123", True),
    ("CINTHIA SANCHES BOTELHO TOJEIRO",         "TEACHER", "cinthia_tojeiro@samba.edvance",   "Prof@123", True),
    ("EVANDRO HENRIQUE DA SILVA FERREIRA",      "TEACHER", "evandro_ferreira@samba.edvance",  "Prof@123", True),
    ("FERNANDO PEREIRA GODOI",                  "TEACHER", "fernando_godoi@samba.edvance",    "Prof@123", True),
    ("GABRIEL GUIMARAES FERREIRA RAMOS",        "TEACHER", "gabriel_ramos@samba.edvance",     "Prof@123", True),
    ("JEAN MARTINS",                            "TEACHER", "jean_martins@samba.edvance",      "Prof@123", True),
    ("LAHYR MORATO KRAHENBUHL NETO",            "TEACHER", "lahyr_neto@samba.edvance",        "Prof@123", True),
    ("LEANDRO JOSE GUARNETTI",                  "TEACHER", "leandro_guarnetti@samba.edvance", "Prof@123", True),
    ("LETICIA ZAFRED PAIVA",                    "TEACHER", "leticia_paiva@samba.edvance",     "Prof@123", True),
    ("LILIAN CRISTIANE PISANO",                 "TEACHER", "lilian_pisano@samba.edvance",     "Prof@123", True),
    ("LUCIANE DUARTE PEROTTA",                  "TEACHER", "luciane_perotta@samba.edvance",   "Prof@123", True),
    ("LUIS GUSTAVO DE SOUZA ZECA",              "TEACHER", "luis_zeca@samba.edvance",         "Prof@123", True),
    ("MARCIA AP. CORREA RODRIGUES",             "TEACHER", "marcia_rodrigues@samba.edvance",  "Prof@123", True),
    ("MARIA BENEDITA MOREIRA",                  "TEACHER", "maria_moreira@samba.edvance",     "Prof@123", True),
    ("MARIA FERNANDA BRIGUETI LOURENCO",        "TEACHER", "maria_lourenco@samba.edvance",    "Prof@123", True),
    ("MARISA ALVES DA SILVA",                   "TEACHER", "marisa_silva@samba.edvance",      "Prof@123", True),
    ("MATHEUS LUIS DE CAMPOS MIELI",            "TEACHER", "matheus_mieli@samba.edvance",     "Prof@123", True),
    ("MICHAEL JORDAO MILIANO DOS SANTOS",       "TEACHER", "michael_santos@samba.edvance",    "Prof@123", True),
    ("PAMELA CAROLINE EVARISTO",                "TEACHER", "pamela_evaristo@samba.edvance",   "Prof@123", True),
    ("PATRICIA STEVANATO DE OLIVEIRA",          "TEACHER", "patricia_oliveira@samba.edvance", "Prof@123", True),
    ("REGINA GENESINI IAYAR",                   "TEACHER", "regina_iayar@samba.edvance",      "Prof@123", True),
    ("ROSANGELA TEREZINHA TICIANELLI PIRES",    "TEACHER", "rosangela_pires@samba.edvance",   "Prof@123", True),
    ("SANDRA APARECIDA BARONI FONSECA",         "TEACHER", "sandra_fonseca@samba.edvance",    "Prof@123", True),
    ("SERGIA MARIA MOREIRA MACHADO",            "TEACHER", "sergia_machado@samba.edvance",    "Prof@123", True),
    ("TERESA CRISTINA",                         "TEACHER", "teresa_cristina@samba.edvance",   "Prof@123", True),
    ("THIAGO STEFANIN",                         "TEACHER", "thiago_stefanin@samba.edvance",   "Prof@123", True),
    ("VALERIA R. C. BOSCO",                     "TEACHER", "valeria_bosco@samba.edvance",     "Prof@123", True),
    ("VANIA MARIA THEODORO PINHEIRO",           "TEACHER", "vania_pinheiro@samba.edvance",    "Prof@123", True),
    ("VINICIUS BERTUZZO LIMA",                  "TEACHER", "vinicius_lima@samba.edvance",     "Prof@123", True),
    ("VITOR BONJORNO CHAGAS",                   "TEACHER", "vitor_chagas@samba.edvance",      "Prof@123", True),

    # Usuarios demo — sem troca obrigatoria
    ("Coordenador Demo",        "COORDINATOR", "coord@samba.edvance",            "Coord@123", False),
    ("Professor de Matematica", "TEACHER",     "prof.matematica@samba.edvance",  "Prof@123",  False),
    ("Professor de Fisica",     "TEACHER",     "prof.fisica@samba.edvance",      "Prof@123",  False),
]


# ─────────────────────────────────────────────────────────────────────────────
# 2. MATRIZES CURRICULARES — extraidas dos arquivos PEI
# ─────────────────────────────────────────────────────────────────────────────
# Nota: "Ensino Religioso (quando houver demanda)" normalizado para
#       "Ensino Religioso" para evitar nome longo no sistema.

# ── Fundamental — Anos Finais ─────────────────────────────────────────────
# 6o, 7o, 8o, 9o: mesma lista (confirmado no xlsx — todas as series tem
# exatamente as mesmas disciplinas)

_FAF = [
    "Lingua Portuguesa",
    "Lingua Inglesa",
    "Arte",
    "Educacao Fisica",
    "Matematica",
    "Ensino Religioso",
    "Ciencias",
    "Geografia",
    "Historia",
    "Projeto de Vida",
    "OE Matematica",
    "OE Lingua Portuguesa",
    "Tecnologia e Inovacao",
    "Educacao Financeira",
    "Redacao e Leitura",
    "Eletiva",
    "Robotica",
    "Praticas Experimentais",
    "EMA",
]

# ── Ensino Medio ──────────────────────────────────────────────────────────

# 1aA, 1aB, 1aC, 1aD, 1aE
_M1 = [
    "Lingua Portuguesa",
    "Redacao e Leitura",
    "Lingua Inglesa",
    "Arte",
    "Educacao Fisica",
    "Matematica",
    "Educacao Financeira",
    "Biologia",
    "Fisica",
    "Quimica",
    "Filosofia",
    "Geografia",
    "Historia",
    "Projeto de Vida",
    "Praticas Experimentais",
    "OE Matematica",
    "OE Lingua Portuguesa",
    "Eletiva",
    "Robotica",
    "EMA",
]

# 2aA e 2aC
_M2AC = [
    "Lingua Portuguesa",
    "Redacao e Leitura",
    "Lingua Inglesa",
    "Sociologia",
    "Educacao Fisica",
    "Matematica",
    "Educacao Financeira",
    "Biologia",
    "Fisica",
    "Quimica",
    "Programacao",
    "Geografia",
    "Historia",
    "Projeto de Vida",
    "Praticas Experimentais",
    "OE Matematica",
    "OE Lingua Portuguesa",
    "Eletiva",
    "Robotica",
    "Empreendedorismo",
    "EMA",
]

# 2aB
_M2B = [
    "Lingua Portuguesa",
    "Redacao e Leitura",
    "Lingua Inglesa",
    "Sociologia",
    "Educacao Fisica",
    "Matematica",
    "Educacao Financeira",
    "Biologia",
    "Fisica",
    "Quimica",
    "Arte e Midias Digitais",
    "Geografia",
    "Historia",
    "Projeto de Vida",
    "Praticas Experimentais",
    "OE Matematica",
    "OE Lingua Portuguesa",
    "Eletiva",
    "Robotica",
    "Lideranca-Oratoria",
    "EMA",
]

# 3aA e 3aB
_M3AB = [
    "Lingua Portuguesa",
    "Redacao e Leitura",
    "Aprofundamento em Sociologia",
    "Aprofundamento em Geografia",
    "Educacao Fisica",
    "Matematica",
    "Aprofundamento em Filosofia",
    "Fisica",
    "Atualidades",
    "Ingles",
    "Historia",
    "Projeto de Vida",
    "Praticas Experimentais",
    "OE Matematica",
    "OE Lingua Portuguesa",
    "Eletiva",
    "Robotica",
    "EMA",
]

# 3aC e 3aD
_M3CD = [
    "Lingua Portuguesa",
    "Redacao e Leitura",
    "Aprofundamento em Quimica",
    "Aprofundamento em Biologia",
    "Educacao Fisica",
    "Matematica",
    "Empreendedorismo",
    "Fisica",
    "Programacao",
    "Ingles",
    "Historia",
    "Projeto de Vida",
    "Praticas Experimentais",
    "OE Matematica",
    "OE Lingua Portuguesa",
    "Eletiva",
    "Robotica",
    "EMA",
]


# ─────────────────────────────────────────────────────────────────────────────
# 3. TURMAS
# (nivel, ano, label_serie, secao, nome_exibicao, lista_disciplinas)
# ─────────────────────────────────────────────────────────────────────────────

CLASSES_DATA = [
    # Ensino Medio — 1a serie (A-E, mesma matriz)
    (EducationLevel.MEDIO, 1, "1a", "A", "1aA", _M1),
    (EducationLevel.MEDIO, 1, "1a", "B", "1aB", _M1),
    (EducationLevel.MEDIO, 1, "1a", "C", "1aC", _M1),
    (EducationLevel.MEDIO, 1, "1a", "D", "1aD", _M1),
    (EducationLevel.MEDIO, 1, "1a", "E", "1aE", _M1),
    # Ensino Medio — 2a serie
    (EducationLevel.MEDIO, 2, "2a", "A", "2aA", _M2AC),
    (EducationLevel.MEDIO, 2, "2a", "B", "2aB", _M2B),
    (EducationLevel.MEDIO, 2, "2a", "C", "2aC", _M2AC),
    # Ensino Medio — 3a serie
    (EducationLevel.MEDIO, 3, "3a", "A", "3aA", _M3AB),
    (EducationLevel.MEDIO, 3, "3a", "B", "3aB", _M3AB),
    (EducationLevel.MEDIO, 3, "3a", "C", "3aC", _M3CD),
    (EducationLevel.MEDIO, 3, "3a", "D", "3aD", _M3CD),
    # Ensino Fundamental — 6o ano
    (EducationLevel.FUNDAMENTAL, 6, "6o", "A", "6oA", _FAF),
    (EducationLevel.FUNDAMENTAL, 6, "6o", "B", "6oB", _FAF),
    # Ensino Fundamental — 7o ano
    (EducationLevel.FUNDAMENTAL, 7, "7o", "A", "7oA", _FAF),
    (EducationLevel.FUNDAMENTAL, 7, "7o", "B", "7oB", _FAF),
    # Ensino Fundamental — 8o ano
    (EducationLevel.FUNDAMENTAL, 8, "8o", "A", "8oA", _FAF),
    (EducationLevel.FUNDAMENTAL, 8, "8o", "B", "8oB", _FAF),
    (EducationLevel.FUNDAMENTAL, 8, "8o", "C", "8oC", _FAF),
    # Ensino Fundamental — 9o ano
    (EducationLevel.FUNDAMENTAL, 9, "9o", "A", "9oA", _FAF),
    (EducationLevel.FUNDAMENTAL, 9, "9o", "B", "9oB", _FAF),
    (EducationLevel.FUNDAMENTAL, 9, "9o", "C", "9oC", _FAF),
]


# ─────────────────────────────────────────────────────────────────────────────
# 4. HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _get_or_create_role(db: Session, name: str) -> Role:
    role = db.query(Role).filter(Role.name == name).first()
    if not role:
        role = Role(name=name)
        db.add(role); db.flush()
    return role


def _get_or_create_user(
    db: Session, name: str, email: str, password: str,
    role_names: list[str], must_change_password: bool = False,
) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            name=name, email=email,
            password_hash=hash_password(password),
            is_active=True,
            must_change_password=must_change_password,
            created_at=datetime.utcnow(),
        )
        db.add(user); db.flush()
        print(f"  + {email}")
    existing = {r.name for r in user.roles}
    for rname in role_names:
        if rname not in existing:
            user.roles.append(_get_or_create_role(db, rname))
    return user


def _get_or_create_discipline(db: Session, name: str) -> Discipline:
    d = db.query(Discipline).filter(Discipline.name == name).first()
    if not d:
        d = Discipline(name=name)
        db.add(d); db.flush()
    return d


def _get_or_create_grade(
    db: Session, level: EducationLevel, year: int, label: str,
) -> SchoolGrade:
    g = db.query(SchoolGrade).filter_by(level=level, year_number=year).first()
    if not g:
        g = SchoolGrade(level=level, year_number=year, label=label)
        db.add(g); db.flush()
    return g


def _get_or_create_section(db: Session, label: str) -> ClassSection:
    s = db.query(ClassSection).filter_by(label=label).first()
    if not s:
        s = ClassSection(label=label)
        db.add(s); db.flush()
    return s


def _get_or_create_class(
    db: Session, grade: SchoolGrade, section: ClassSection, name: str,
) -> SchoolClass:
    sc = db.query(SchoolClass).filter_by(
        grade_id=grade.id, section_id=section.id,
    ).first()
    if not sc:
        sc = SchoolClass(grade_id=grade.id, section_id=section.id, name=name)
        db.add(sc); db.flush()
        print(f"  + Turma {name}")
    return sc


# ─────────────────────────────────────────────────────────────────────────────
# 5. SEED POR DOMINIO
# ─────────────────────────────────────────────────────────────────────────────

def seed_roles(db: Session) -> None:
    print("\n[roles]")
    for name in ["ADMIN", "COORDINATOR", "TEACHER", "student"]:
        _get_or_create_role(db, name)
    print("  OK")


def seed_users(db: Session) -> None:
    print("\n[usuarios]")
    for name, role, email, senha, must_change in USERS_DATA:
        roles = ["ADMIN", "COORDINATOR"] if role == "ADMIN" else [role]
        _get_or_create_user(db, name, email, senha, roles, must_change)


def seed_school_structure(db: Session) -> None:
    print("\n[estrutura escolar]")

    # Coleta todas as disciplinas unicas das matrizes
    all_disc_names: set[str] = set()
    for *_, discs in CLASSES_DATA:
        all_disc_names.update(discs)

    disc_map: dict[str, Discipline] = {
        n: _get_or_create_discipline(db, n) for n in sorted(all_disc_names)
    }
    print(f"  + {len(disc_map)} disciplinas")

    # Secoes A-E
    sections = {l: _get_or_create_section(db, l) for l in "ABCDE"}

    # Grades e turmas
    grades: dict[tuple, SchoolGrade] = {}
    turmas_criadas = 0
    turmas_atualizadas = 0

    for level, year, label_grade, section_letter, name_display, disc_list in CLASSES_DATA:
        gkey = (level, year)
        if gkey not in grades:
            grades[gkey] = _get_or_create_grade(db, level, year, label_grade)

        sc = _get_or_create_class(
            db, grades[gkey], sections[section_letter], name_display,
        )
        db.flush()

        # Vincula disciplinas (idempotente)
        existing_ids = {d.id for d in sc.disciplines}
        added = 0
        for disc_name in disc_list:
            d = disc_map.get(disc_name)
            if d and d.id not in existing_ids:
                sc.disciplines.append(d)
                existing_ids.add(d.id)
                added += 1

        if added:
            turmas_atualizadas += 1
        else:
            turmas_criadas += 1

    print(f"  + {turmas_atualizadas} turmas com disciplinas vinculadas/atualizadas")
    print(f"    {turmas_criadas} turmas ja estavam completas")


# ─────────────────────────────────────────────────────────────────────────────
# 6. ENTRY POINTS
# ─────────────────────────────────────────────────────────────────────────────

def run_seed(db: Session) -> None:
    print("=" * 60)
    print("  SAMBA Simulator — Seed de Producao")
    print("  EE Prof. Christino Cabral")
    print("=" * 60)

    seed_roles(db)
    seed_users(db)
    seed_school_structure(db)

    db.commit()

    n_coord = sum(1 for _, r, *_ in USERS_DATA if r == "COORDINATOR")
    n_prof  = sum(1 for _, r, *_ in USERS_DATA if r == "TEACHER")

    print("\n" + "=" * 60)
    print("  Seed concluido com sucesso!")
    print(f"  {len(USERS_DATA)} usuarios  |  {len(CLASSES_DATA)} turmas")
    print()
    print("  Acesso permanente:")
    print("  root@samba.edvance            ->  R7D46S*98/4pwd")
    print()
    print("  Acesso rapido (sem troca obrigatoria):")
    print("  coord@samba.edvance           ->  Coord@123")
    print("  prof.matematica@samba.edvance ->  Prof@123")
    print("  prof.fisica@samba.edvance     ->  Prof@123")
    print()
    print(f"  {n_coord} coordenadores reais  ->  Coord@123  (troca obrig.)")
    print(f"  {n_prof - 2} professores reais  ->  Prof@123   (troca obrig.)")
    print("=" * 60)


def main() -> None:
    db = SessionLocal()
    try:
        run_seed(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()