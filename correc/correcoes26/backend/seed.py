# -*- coding: utf-8 -*-
"""
app/core/seed.py — Seed de Produção
=====================================
EE Prof. Christino Cabral
  • 41 usuários reais (1 ROOT, 5 coordenadores, 35 professores)
  • 22 turmas reais com disciplinas vinculadas conforme matrizes PEI
  • must_change_password=True para todos exceto ROOT
  • Idempotente: rodar novamente não duplica dados
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
# 1. USUÁRIOS
# ─────────────────────────────────────────────────────────────────────────────

USERS_DATA = [
    # (nome, role, email, senha_provisória, must_change_password)
    ("ROOT",                                    "ADMIN",       "root@samba.edvance",              "R7D46S*98/4pwd", False),
    ("ADAIANE RODRIGUES MARTINS",               "TEACHER",     "adaiane_martins@samba.edvance",   "Prof@123",       True),
    ("ALINE CRISTIANE ZORZI",                   "COORDINATOR", "aline_zorzi@samba.edvance",       "Coord@123",      True),
    ("ANA CAROLINA DE FREITAS NUNES HARTEN",    "TEACHER",     "ana_harten@samba.edvance",        "Prof@123",       True),
    ("ANA LÚCIA MARIANO DOS SANTOS",            "TEACHER",     "ana_santos@samba.edvance",        "Prof@123",       True),
    ("ANGÉLICA LONGO DE CAMPOS",                "TEACHER",     "angelica_campos@samba.edvance",   "Prof@123",       True),
    ("CAMILA CHIQUITO PALHARES",                "TEACHER",     "camila_palhares@samba.edvance",   "Prof@123",       True),
    ("CARLA REGINA SPARAPAM DA SILVA",          "COORDINATOR", "carla_silva@samba.edvance",       "Coord@123",      True),
    ("CÉSAR AUGUSTO GABURI",                    "TEACHER",     "cesar_gaburi@samba.edvance",      "Prof@123",       True),
    ("CINTHIA SANCHES BOTELHO TOJEIRO",         "TEACHER",     "cinthia_tojeiro@samba.edvance",   "Prof@123",       True),
    ("EVANDRO HENRIQUE DA SILVA FERREIRA",      "TEACHER",     "evandro_ferreira@samba.edvance",  "Prof@123",       True),
    ("FABIO ANGELO AGUIAR",                     "COORDINATOR", "fabio_aguiar@samba.edvance",      "Coord@123",      True),
    ("FERNANDO PEREIRA GODOI",                  "TEACHER",     "fernando_godoi@samba.edvance",    "Prof@123",       True),
    ("GABRIEL GUIMARÃES FERREIRA RAMOS",        "TEACHER",     "gabriel_ramos@samba.edvance",     "Prof@123",       True),
    ("GILCELENE JANAINA RODRIGUES CARDOSO",     "COORDINATOR", "gilcelene_cardoso@samba.edvance", "Coord@123",      True),
    ("JEAN MARTINS",                            "TEACHER",     "jean_martins@samba.edvance",      "Prof@123",       True),
    ("LAHYR MORATO KRAHENBUHL NETO",            "TEACHER",     "lahyr_neto@samba.edvance",        "Prof@123",       True),
    ("LEANDRO JOSÉ GUARNETTI",                  "TEACHER",     "leandro_guarnetti@samba.edvance", "Prof@123",       True),
    ("LETÍCIA ZAFRED PAIVA",                    "TEACHER",     "leticia_paiva@samba.edvance",     "Prof@123",       True),
    ("LILIAN CRISTIANE PISANO",                 "TEACHER",     "lilian_pisano@samba.edvance",     "Prof@123",       True),
    ("LUCIANE DUARTE PEROTTA",                  "TEACHER",     "luciane_perotta@samba.edvance",   "Prof@123",       True),
    ("LUÍS GUSTAVO DE SOUZA ZECA",              "TEACHER",     "luis_zeca@samba.edvance",         "Prof@123",       True),
    ("MÁRCIA AP. CORRÊA RODRIGUES",             "TEACHER",     "marcia_rodrigues@samba.edvance",  "Prof@123",       True),
    ("MARIA BENEDITA MOREIRA",                  "TEACHER",     "maria_moreira@samba.edvance",     "Prof@123",       True),
    ("MARIA FERNANDA BRIGUETI LOURENÇO",        "TEACHER",     "maria_lourenco@samba.edvance",    "Prof@123",       True),
    ("MARISA ALVES DA SILVA",                   "TEACHER",     "marisa_silva@samba.edvance",      "Prof@123",       True),
    ("MATHEUS LUIS DE CAMPOS MIELI",            "TEACHER",     "matheus_mieli@samba.edvance",     "Prof@123",       True),
    ("MICHAEL JORDÃO MILIANO DOS SANTOS",       "TEACHER",     "michael_santos@samba.edvance",    "Prof@123",       True),
    ("PÂMELA CAROLINE EVARISTO",                "TEACHER",     "pamela_evaristo@samba.edvance",   "Prof@123",       True),
    ("PATRÍCIA STEVANATO DE OLIVEIRA",          "TEACHER",     "patricia_oliveira@samba.edvance", "Prof@123",       True),
    ("RAUL DE SOUZA HOFFMANN",                  "COORDINATOR", "raul_hoffmann@samba.edvance",     "Coord@123",      True),
    ("REGINA GENESINI IAYAR",                   "TEACHER",     "regina_iayar@samba.edvance",      "Prof@123",       True),
    ("ROSANGELA TEREZINHA TICIANELLI PIRES",    "TEACHER",     "rosangela_pires@samba.edvance",   "Prof@123",       True),
    ("SANDRA APARECIDA BARONI FONSECA",         "TEACHER",     "sandra_fonseca@samba.edvance",    "Prof@123",       True),
    ("SÉRGIA MARIA MOREIRA MACHADO",            "TEACHER",     "sergia_machado@samba.edvance",    "Prof@123",       True),
    ("TERESA CRISTINA",                         "TEACHER",     "teresa_cristina@samba.edvance",   "Prof@123",       True),
    ("THIAGO STEFANIN",                         "TEACHER",     "thiago_stefanin@samba.edvance",   "Prof@123",       True),
    ("VALÉRIA R. C. BOSCO",                     "TEACHER",     "valeria_bosco@samba.edvance",     "Prof@123",       True),
    ("VÂNIA MARIA THEODORO PINHEIRO",           "TEACHER",     "vania_pinheiro@samba.edvance",    "Prof@123",       True),
    ("VINÍCIUS BERTUZZO LIMA",                  "TEACHER",     "vinicius_lima@samba.edvance",     "Prof@123",       True),
    ("VITOR BONJORNO CHAGAS",                   "TEACHER",     "vitor_chagas@samba.edvance",      "Prof@123",       True),
]


# ─────────────────────────────────────────────────────────────────────────────
# 2. DISCIPLINAS — agrupadas por matriz
# ─────────────────────────────────────────────────────────────────────────────

_M1 = [          # 1ª série A-E (Ensino Médio)
    "Língua Portuguesa", "Redação e Leitura", "Língua Inglesa", "Arte",
    "Educação Física", "Matemática", "Educação Financeira", "Biologia",
    "Física", "Química", "Filosofia", "Geografia", "História",
    "Projeto de Vida", "Práticas Experimentais",
    "OE Matemática", "OE Língua Portuguesa", "Eletiva", "Robótica", "EMA",
]

_M2AC = [        # 2ª série A e C
    "Língua Portuguesa", "Redação e Leitura", "Língua Inglesa", "Sociologia",
    "Educação Física", "Matemática", "Educação Financeira", "Biologia",
    "Física", "Química", "Programação", "Geografia", "História",
    "Projeto de Vida", "Práticas Experimentais",
    "OE Matemática", "OE Língua Portuguesa", "Eletiva", "Robótica",
    "Empreendedorismo", "EMA",
]

_M2B = [         # 2ª série B
    "Língua Portuguesa", "Redação e Leitura", "Língua Inglesa", "Sociologia",
    "Educação Física", "Matemática", "Educação Financeira", "Biologia",
    "Física", "Química", "Arte e Mídias Digitais", "Geografia", "História",
    "Projeto de Vida", "Práticas Experimentais",
    "OE Matemática", "OE Língua Portuguesa", "Eletiva", "Robótica",
    "Liderança-Oratória", "EMA",
]

_M3AB = [        # 3ª série A e B
    "Língua Portuguesa", "Redação e Leitura",
    "Aprofundamento em Sociologia", "Aprofundamento em Geografia",
    "Educação Física", "Matemática", "Aprofundamento em Filosofia",
    "Física", "Atualidades", "Inglês", "História",
    "Projeto de Vida", "Práticas Experimentais",
    "OE Matemática", "OE Língua Portuguesa", "Eletiva", "Robótica", "EMA",
]

_M3CD = [        # 3ª série C e D
    "Língua Portuguesa", "Redação e Leitura",
    "Aprofundamento em Química", "Aprofundamento em Biologia",
    "Educação Física", "Matemática", "Empreendedorismo",
    "Física", "Programação", "Inglês", "História",
    "Projeto de Vida", "Práticas Experimentais",
    "OE Matemática", "OE Língua Portuguesa", "Eletiva", "Robótica", "EMA",
]

_FAF = [         # Anos Finais — 6º ao 9º (todas as turmas)
    "Língua Portuguesa", "Língua Inglesa", "Arte", "Educação Física",
    "Matemática", "Ensino Religioso", "Ciências", "Geografia", "História",
    "Projeto de Vida", "OE Matemática", "OE Língua Portuguesa",
    "Tecnologia e Inovação", "Educação Financeira", "Redação e Leitura",
    "Eletiva", "Robótica", "Práticas Experimentais", "EMA",
]


# ─────────────────────────────────────────────────────────────────────────────
# 3. TURMAS — (nível, ano, label_série, seção, nome_exibição, disciplinas)
# ─────────────────────────────────────────────────────────────────────────────

CLASSES_DATA = [
    # Ensino Médio — 1ª série
    (EducationLevel.MEDIO,       1, "1ª", "A", "1ªA", _M1),
    (EducationLevel.MEDIO,       1, "1ª", "B", "1ªB", _M1),
    (EducationLevel.MEDIO,       1, "1ª", "C", "1ªC", _M1),
    (EducationLevel.MEDIO,       1, "1ª", "D", "1ªD", _M1),
    (EducationLevel.MEDIO,       1, "1ª", "E", "1ªE", _M1),
    # Ensino Médio — 2ª série
    (EducationLevel.MEDIO,       2, "2ª", "A", "2ªA", _M2AC),
    (EducationLevel.MEDIO,       2, "2ª", "B", "2ªB", _M2B),
    (EducationLevel.MEDIO,       2, "2ª", "C", "2ªC", _M2AC),
    # Ensino Médio — 3ª série
    (EducationLevel.MEDIO,       3, "3ª", "A", "3ªA", _M3AB),
    (EducationLevel.MEDIO,       3, "3ª", "B", "3ªB", _M3AB),
    (EducationLevel.MEDIO,       3, "3ª", "C", "3ªC", _M3CD),
    (EducationLevel.MEDIO,       3, "3ª", "D", "3ªD", _M3CD),
    # Ensino Fundamental — Anos Finais
    (EducationLevel.FUNDAMENTAL, 6, "6º", "A", "6ºA", _FAF),
    (EducationLevel.FUNDAMENTAL, 6, "6º", "B", "6ºB", _FAF),
    (EducationLevel.FUNDAMENTAL, 7, "7º", "A", "7ºA", _FAF),
    (EducationLevel.FUNDAMENTAL, 7, "7º", "B", "7ºB", _FAF),
    (EducationLevel.FUNDAMENTAL, 8, "8º", "A", "8ºA", _FAF),
    (EducationLevel.FUNDAMENTAL, 8, "8º", "B", "8ºB", _FAF),
    (EducationLevel.FUNDAMENTAL, 8, "8º", "C", "8ºC", _FAF),
    (EducationLevel.FUNDAMENTAL, 9, "9º", "A", "9ºA", _FAF),
    (EducationLevel.FUNDAMENTAL, 9, "9º", "B", "9ºB", _FAF),
    (EducationLevel.FUNDAMENTAL, 9, "9º", "C", "9ºC", _FAF),
]


# ─────────────────────────────────────────────────────────────────────────────
# 4. HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _get_or_create_role(db: Session, name: str) -> Role:
    role = db.query(Role).filter(Role.name == name).first()
    if not role:
        role = Role(name=name)
        db.add(role)
        db.flush()
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
        db.add(user)
        db.flush()
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
        db.add(d)
        db.flush()
    return d


def _get_or_create_grade(db: Session, level: EducationLevel, year: int, label: str) -> SchoolGrade:
    g = db.query(SchoolGrade).filter_by(level=level, year_number=year).first()
    if not g:
        g = SchoolGrade(level=level, year_number=year, label=label)
        db.add(g)
        db.flush()
    return g


def _get_or_create_section(db: Session, label: str) -> ClassSection:
    s = db.query(ClassSection).filter_by(label=label).first()
    if not s:
        s = ClassSection(label=label)
        db.add(s)
        db.flush()
    return s


def _get_or_create_class(
    db: Session, grade: SchoolGrade, section: ClassSection, name: str,
) -> SchoolClass:
    sc = db.query(SchoolClass).filter_by(grade_id=grade.id, section_id=section.id).first()
    if not sc:
        sc = SchoolClass(grade_id=grade.id, section_id=section.id, name=name)
        db.add(sc)
        db.flush()
        print(f"  + Turma {name}")
    return sc


# ─────────────────────────────────────────────────────────────────────────────
# 5. SEED POR DOMÍNIO
# ─────────────────────────────────────────────────────────────────────────────

def seed_roles(db: Session) -> None:
    print("\n[roles]")
    for name in ["ADMIN", "COORDINATOR", "TEACHER", "student"]:
        _get_or_create_role(db, name)
    print("  OK")


def seed_users(db: Session) -> None:
    print("\n[usuários]")
    for name, role, email, senha, must_change in USERS_DATA:
        roles = ["ADMIN", "COORDINATOR"] if role == "ADMIN" else [role]
        _get_or_create_user(db, name, email, senha, roles, must_change)


def seed_school_structure(db: Session) -> None:
    print("\n[estrutura escolar]")

    if db.query(SchoolGrade).first() is not None:
        print("  Estrutura já existe — ignorado (idempotente).")
        return

    # Disciplinas únicas
    all_disc_names: set[str] = set()
    for *_, discs in CLASSES_DATA:
        all_disc_names.update(discs)
    disc_map: dict[str, Discipline] = {
        n: _get_or_create_discipline(db, n) for n in sorted(all_disc_names)
    }
    print(f"  + {len(disc_map)} disciplinas")

    # Seções
    sections = {l: _get_or_create_section(db, l) for l in "ABCDE"}

    # Grades e turmas
    grades: dict[tuple, SchoolGrade] = {}
    for level, year, label_grade, section_letter, name_display, disc_list in CLASSES_DATA:
        gkey = (level, year)
        if gkey not in grades:
            grades[gkey] = _get_or_create_grade(db, level, year, label_grade)

        sc = _get_or_create_class(db, grades[gkey], sections[section_letter], name_display)
        db.flush()

        # Vincular disciplinas
        existing_ids = {d.id for d in sc.disciplines}
        for disc_name in disc_list:
            d = disc_map.get(disc_name)
            if d and d.id not in existing_ids:
                sc.disciplines.append(d)
                existing_ids.add(d.id)

    print(f"  + {len(CLASSES_DATA)} turmas com disciplinas vinculadas")


# ─────────────────────────────────────────────────────────────────────────────
# 6. ENTRY POINTS
# ─────────────────────────────────────────────────────────────────────────────

def run_seed(db: Session) -> None:
    print("=" * 55)
    print("  SAMBA Simulator — Seed de Produção")
    print("  EE Prof. Christino Cabral")
    print("=" * 55)

    seed_roles(db)
    seed_users(db)
    seed_school_structure(db)

    db.commit()

    print("\n" + "=" * 55)
    print("  Seed concluído!")
    print(f"  {len(USERS_DATA)} usuários  |  {len(CLASSES_DATA)} turmas")
    print()
    print("  root@samba.edvance        →  R7D46S*98/4pwd")
    print("  Coordenadores             →  Coord@123  (troca obrig.)")
    print("  Professores               →  Prof@123   (troca obrig.)")
    print("=" * 55)


def main() -> None:
    db = SessionLocal()
    try:
        run_seed(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
