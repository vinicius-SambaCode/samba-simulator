"""
===============================================================================
MODELOS BASE DO SISTEMA
===============================================================================

Este arquivo define:

• Base declarativa do SQLAlchemy
• Enums institucionais
• Tabelas principais do sistema
• Relacionamentos N:N e 1:N
• Índices estratégicos
• Configurações de integridade referencial

IMPORTANTE:
Este arquivo é o coração do banco de dados.
Qualquer erro aqui impacta todo o sistema.

===============================================================================
"""

# =============================================================================
# IMPORTS
# =============================================================================

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Enum,
    Text,
    Table,
    DateTime,
    func
)
from sqlalchemy.orm import relationship, declarative_base
import enum


# =============================================================================
# BASE DECLARATIVA
# =============================================================================

Base = declarative_base()


# =============================================================================
# ENUMS INSTITUCIONAIS
# =============================================================================

class DifficultyEnum(str, enum.Enum):
    """
    Níveis de dificuldade pedagógica.
    Usado na geração de provas e blueprint.
    """
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class ItemTypeEnum(str, enum.Enum):
    """
    Tipo da questão.
    Permite expansão futura.
    """
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    DISCURSIVE = "DISCURSIVE"
    NUMERIC = "NUMERIC"


# =============================================================================
# TABELA DE ASSOCIAÇÃO USER <-> ROLE (N:N)
# =============================================================================

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


# =============================================================================
# ROLE
# =============================================================================

class Role(Base):
    """
    Define papéis institucionais.
    Ex:
    - ADMIN
    - COORDINATOR
    - TEACHER
    """

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False, index=True)

    users = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles"
    )

    def __repr__(self):
        return f"<Role(name={self.name})>"


# =============================================================================
# USER
# =============================================================================

class User(Base):
    """
    Usuário do sistema.
    Pode ter múltiplos papéis (RBAC real).
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    roles = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users"
    )

    items = relationship(
        "Item",
        back_populates="owner",
        cascade="all, delete"
    )

    def __repr__(self):
        return f"<User(email={self.email})>"


# =============================================================================
# DISCIPLINE
# =============================================================================

class Discipline(Base):
    """
    Disciplina curricular.
    Ex:
    - Matemática
    - Física
    - Biologia
    """

    __tablename__ = "disciplines"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True, nullable=False, index=True)

    skills = relationship(
        "Skill",
        back_populates="discipline",
        cascade="all, delete"
    )

    items = relationship(
        "Item",
        back_populates="discipline",
        cascade="all, delete"
    )

    def __repr__(self):
        return f"<Discipline(name={self.name})>"


# =============================================================================
# SKILL
# =============================================================================

class Skill(Base):
    """
    Habilidade vinculada a uma disciplina.
    Ex:
    - EM13MAT101
    - Resolver equações do 2º grau
    """

    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)

    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)

    discipline_id = Column(
        Integer,
        ForeignKey("disciplines.id", ondelete="CASCADE"),
        nullable=False
    )

    discipline = relationship(
        "Discipline",
        back_populates="skills"
    )

    items = relationship(
        "Item",
        back_populates="skill"
    )

    def __repr__(self):
        return f"<Skill(code={self.code})>"


# =============================================================================
# ITEM (QUESTÃO)
# =============================================================================

class Item(Base):
    """
    Representa uma questão avaliativa.
    Pode ser múltipla escolha, discursiva ou numérica.
    """

    __tablename__ = "items"

    id = Column(Integer, primary_key=True)

    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    discipline_id = Column(
        Integer,
        ForeignKey("disciplines.id", ondelete="CASCADE"),
        nullable=False
    )

    skill_id = Column(
        Integer,
        ForeignKey("skills.id", ondelete="SET NULL"),
        nullable=True
    )

    serie = Column(String(20), nullable=False, index=True)

    difficulty = Column(
        Enum(DifficultyEnum),
        nullable=False
    )

    item_type = Column(
        Enum(ItemTypeEnum),
        nullable=False
    )

    stem = Column(Text, nullable=False)

    options_json = Column(Text, nullable=True)
    numeric_answer = Column(String(50), nullable=True)
    media_url = Column(String(255), nullable=True)

    latex = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    owner = relationship("User", back_populates="items")
    discipline = relationship("Discipline", back_populates="items")
    skill = relationship("Skill", back_populates="items")

    def __repr__(self):
        return f"<Item(id={self.id}, difficulty={self.difficulty})>"