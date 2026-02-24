"""
==========================================================
BASE MODELS DO SISTEMA (VERSÃO COM MÚLTIPLOS PAPÉIS)
==========================================================

Define:

• Enums de domínio
• Modelos SQLAlchemy
• Relacionamentos
• Sistema RBAC N:N
• Blueprint (estrutura de prova/simulado)

Arquitetura:

users
roles
user_roles (N:N)
blueprints
"""

# ==========================================================
# IMPORTS
# ==========================================================

from enum import Enum as PyEnum
from sqlalchemy import Enum as SQLEnum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    ForeignKey,
    UniqueConstraint,
    Table
)

from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.db import Base


# ==========================================================
# ENUMS
# ==========================================================

class BimesterEnum(str, PyEnum):
    B1 = "1º BIMESTRE"
    B2 = "2º BIMESTRE"
    B3 = "3º BIMESTRE"
    B4 = "4º BIMESTRE"


class AreaConhecimentoEnum(str, PyEnum):
    LINGUAGENS = "Linguagens e Códigos"
    MATEMATICA = "Matemática"
    CIENCIAS_NATUREZA = "Ciências da Natureza"
    CIENCIAS_HUMANAS = "Ciências Humanas"


class DifficultyEnum(str, PyEnum):
    EASY = "Fácil"
    MEDIUM = "Médio"
    HARD = "Difícil"


class ItemTypeEnum(str, PyEnum):
    MCQ = "Múltipla escolha"
    NUMERIC = "Numérica"
    OPEN = "Aberta"


# ==========================================================
# USER_ROLES (N:N)
# ==========================================================

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)


# ==========================================================
# ROLE
# ==========================================================

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    users = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles"
    )


# ==========================================================
# USER
# ==========================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    name = Column(String(120), nullable=False)

    email = Column(
        String(120),
        nullable=False,
        unique=True,
        index=True
    )

    password_hash = Column(String(255), nullable=False)

    roles = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users"
    )

    is_active = Column(Boolean, default=True)


# ==========================================================
# DISCIPLINE
# ==========================================================

class Discipline(Base):
    __tablename__ = "disciplines"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False, unique=True)


# ==========================================================
# SKILL
# ==========================================================

class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True
    )

    description: Mapped[str] = mapped_column(String(255))


# ==========================================================
# BLUEPRINT (ADICIONADO)
# ==========================================================

class Blueprint(Base):
    """
    Representa um modelo estrutural de prova/simulado.

    Exemplo:
    - Simulado ENEM Matemática 1º ano
    - Avaliação 2º Bimestre Ciências

    Não armazena itens.
    Apenas define uma estrutura organizacional.
    """

    __tablename__ = "blueprints"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )


# ==========================================================
# ITEM
# ==========================================================

class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    discipline_id: Mapped[int] = mapped_column(
        ForeignKey("disciplines.id"),
        nullable=False
    )

    serie: Mapped[str] = mapped_column(String(10), nullable=False)

    skill_id: Mapped[int | None] = mapped_column(
        ForeignKey("skills.id"),
        nullable=True
    )

    difficulty: Mapped[DifficultyEnum] = mapped_column(
        SQLEnum(
            DifficultyEnum,
            name="difficultyenum",
            native_enum=True,
            create_constraint=True
        ),
        nullable=False,
        default=DifficultyEnum.MEDIUM
    )

    item_type: Mapped[ItemTypeEnum] = mapped_column(
        SQLEnum(
            ItemTypeEnum,
            name="itemtypeenum",
            native_enum=True,
            create_constraint=True
        ),
        nullable=False,
        default=ItemTypeEnum.MCQ
    )

    stem: Mapped[str] = mapped_column(Text, nullable=False)
    options_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    numeric_answer: Mapped[str | None] = mapped_column(String(50), nullable=True)
    media_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latex: Mapped[bool] = mapped_column(Boolean, default=False)

    owner = relationship("User")
    discipline = relationship("Discipline")
    skill = relationship("Skill")