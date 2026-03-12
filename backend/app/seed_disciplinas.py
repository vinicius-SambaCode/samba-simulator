#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
seed_disciplinas.py
====================
Popula o banco com as disciplinas (componentes curriculares) extraídas
das grades curriculares oficiais:

  EF.pdf  → Ensino Fundamental (Anos Finais: 6º ao 9º ano)
  EM.pdf  → Ensino Médio (1ª a 3ª série)

Execute dentro do container:
  docker compose exec api python app/seed_disciplinas.py

Ou localmente (com DATABASE_URL configurada):
  python seed_disciplinas.py

Idempotente: disciplinas já existentes são ignoradas.
"""

from __future__ import annotations
import sys
import os

# Ajuste de path para rodar tanto como script avulso quanto via docker exec
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.models.models import Discipline


# =============================================================================
# Disciplinas — Ensino Fundamental (Anos Finais)
# Grade curricular SEDUC-SP / EF.pdf (última página)
# =============================================================================
DISCIPLINAS_EF = [
    "Língua Portuguesa",
    "Arte",
    "Educação Física",
    "Língua Inglesa",
    "Matemática",
    "Ciências",
    "Geografia",
    "História",
    "Ensino Religioso",
    "Tecnologia e Inovação",            # componente curricular eletivo EF
]


# =============================================================================
# Disciplinas — Ensino Médio
# Grade curricular SEDUC-SP / EM.pdf (últimas duas tabelas)
# Itinerários Formativas incluídos conforme grade
# =============================================================================
DISCIPLINAS_EM = [
    # Formação Geral Básica
    "Língua Portuguesa",                # já presente no EF — idempotente
    "Arte",
    "Educação Física",
    "Língua Inglesa",
    "Matemática",
    "Física",
    "Química",
    "Biologia",
    "História",
    "Geografia",
    "Sociologia",
    "Filosofia",
    # Projeto de Vida (componente obrigatório EM)
    "Projeto de Vida",
    # Itinerários Formativos — Linguagens e suas Tecnologias
    "Estudos de Língua e Cultura",
    "Comunicação e Expressão Criativa",
    # Itinerários Formativos — Ciências da Natureza e suas Tecnologias
    "Investigação Científica",
    # Itinerários Formativos — Matemática e suas Tecnologias
    "Matemática Aplicada",
    # Itinerários Formativos — Ciências Humanas e Sociais Aplicadas
    "Mundo do Trabalho",
    # Itinerário Formativo — Tecnologia (Técnico integrado / Exatas)
    "Programação",
    "Tecnologia e Inovação",            # já presente no EF — idempotente
    # Eletivas comuns
    "Redação e Argumentação",
    "Empreendedorismo",
]


# =============================================================================
# Merge sem duplicatas, mantendo ordem lógica
# =============================================================================
TODAS_AS_DISCIPLINAS: list[str] = []
seen: set[str] = set()
for nome in DISCIPLINAS_EF + DISCIPLINAS_EM:
    if nome not in seen:
        TODAS_AS_DISCIPLINAS.append(nome)
        seen.add(nome)


# =============================================================================
# Seed
# =============================================================================
def seed_disciplinas(db: Session) -> None:
    criadas   = []
    existentes = []

    for nome in TODAS_AS_DISCIPLINAS:
        disc = db.query(Discipline).filter(Discipline.name == nome).first()
        if not disc:
            db.add(Discipline(name=nome))
            criadas.append(nome)
        else:
            existentes.append(nome)

    db.commit()

    print(f"\n📚 Seed de Disciplinas")
    print(f"{'─' * 50}")

    if criadas:
        print(f"\n  ✅ Criadas ({len(criadas)}):")
        for n in criadas:
            print(f"      + {n}")

    if existentes:
        print(f"\n  ✔  Já existiam ({len(existentes)}):")
        for n in existentes:
            print(f"      · {n}")

    total = db.query(Discipline).count()
    print(f"\n  📊 Total no banco: {total} disciplinas")
    print(f"{'─' * 50}\n")


def main() -> None:
    db = SessionLocal()
    try:
        seed_disciplinas(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
