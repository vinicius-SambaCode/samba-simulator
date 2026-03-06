# =============================================================================
# app/models/base_models.py
# =============================================================================
#
# RESPONSABILIDADE DESTE ARQUIVO:
#   - Definir a BASE DECLARATIVA ÚNICA do sistema (Base)
#   - Definir os models principais: User, Role, Discipline, Skill, Item
#   - Ser o ponto central que o Alembic usa para detectar TODAS as tabelas
#
# POR QUE UMA BASE ÚNICA?
#   O Alembic precisa importar UMA Base que "conheça" todos os models.
#   Se houver duas bases separadas, tabelas ficam invisíveis para as migrations.
#   Portanto, TODOS os models do sistema herdam desta Base aqui definida.
#
# HISTÓRICO:
#   v1 — usava declarative_base() do SQLAlchemy 1.x
#   v2 — migrado para DeclarativeBase do SQLAlchemy 2.x (sintaxe moderna)
#        db.py passa a importar esta Base em vez de criar a sua própria
# =============================================================================

from __future__ import annotations

# --- SQLAlchemy 2.x imports ---
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
    func,
)
from sqlalchemy.orm import (
    relationship,
    DeclarativeBase,   # SQLAlchemy 2.x — substitui declarative_base()
    Mapped,            # para type hints opcionais futuros
    mapped_column,
)

import enum


# =============================================================================
# BASE DECLARATIVA ÚNICA
# =============================================================================
# Esta é a única Base do sistema.
# Todos os models (neste arquivo e em school.py, exam.py, etc.)
# herdam desta classe.
#
# IMPORTANTE: db.py NÃO deve criar outra Base.
#             Ele deve importar esta daqui:
#               from app.models.base_models import Base
# =============================================================================

class Base(DeclarativeBase):
    """
    Base declarativa central do SAMBA Simulator.
    Herdar desta classe registra automaticamente a tabela no metadata,
    tornando-a visível para o Alembic e para o SQLAlchemy.
    """
    pass


# =============================================================================
# ENUMS INSTITUCIONAIS
# =============================================================================

class DifficultyEnum(str, enum.Enum):
    """
    Nível de dificuldade pedagógica de uma questão.
    Usado na geração de simulados e no blueprint curricular.
    """
    EASY   = "EASY"
    MEDIUM = "MEDIUM"
    HARD   = "HARD"


class ItemTypeEnum(str, enum.Enum):
    """
    Tipo da questão.
    MULTIPLE_CHOICE: alternativas A-D ou A-E (padrão Provas Paulistas)
    DISCURSIVE:      resposta aberta (não usado no simulado atual)
    NUMERIC:         resposta numérica (não usado no simulado atual)
    """
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    DISCURSIVE      = "DISCURSIVE"
    NUMERIC         = "NUMERIC"


# =============================================================================
# TABELA DE ASSOCIAÇÃO USER <-> ROLE  (relação N:N)
# =============================================================================
# Um usuário pode ter múltiplos papéis (ex.: ADMIN + COORDINATOR)
# Um papel pode pertencer a múltiplos usuários
#
# Esta tabela intermediária não tem model próprio — é gerenciada
# automaticamente pelo SQLAlchemy via relationship(secondary=...)
# =============================================================================

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "user_id",
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


# =============================================================================
# MODEL: Role (Papel/Perfil de acesso)
# =============================================================================

class Role(Base):
    """
    Define os papéis institucionais do sistema.

    Papéis atuais:
      ADMIN       — acesso total (usuário root criado pelo seed)
      COORDINATOR — abre simulados, acompanha progresso, gera PDFs
      TEACHER     — alimenta questões no período de coleta

    O sistema usa RBAC (Role-Based Access Control):
    as permissões são verificadas pelo decorador require_role()
    em app/core/deps.py
    """
    __tablename__ = "roles"

    id   = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False, index=True)

    # Relacionamento reverso: quais usuários têm este papel
    users = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
    )

    def __repr__(self):
        return f"<Role(name={self.name})>"


# =============================================================================
# MODEL: User (Usuário do sistema)
# =============================================================================

class User(Base):
    """
    Usuário autenticado do SAMBA Simulator.

    Campos principais:
      email         — login único no sistema
      password_hash — senha armazenada com bcrypt (nunca em texto puro)
      is_active     — desativação lógica (não apaga o registro)
      created_at    — timestamp automático de criação

    Relacionamentos:
      roles → papéis do usuário (N:N via user_roles)
      items → questões do banco de itens de sua autoria
    """
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True)
    name          = Column(String(100), nullable=False)
    email         = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    # Papéis do usuário (RBAC)
    roles = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
    )

    # Questões criadas por este usuário
    items = relationship(
        "Item",
        back_populates="owner",
        cascade="all, delete",
    )

    def __repr__(self):
        return f"<User(email={self.email})>"


# =============================================================================
# MODEL: Discipline (Disciplina curricular)
# =============================================================================

class Discipline(Base):
    """
    Representa uma disciplina do currículo escolar.

    Exemplos: Matemática, Física, Química, Língua Portuguesa...

    Alinhamento:
      As disciplinas são baseadas na BNCC e nas matrizes de referência
      das Provas Paulistas (SEDUC-SP).

    Relacionamentos:
      skills → habilidades vinculadas a esta disciplina
      items  → questões do banco de itens desta disciplina
    """
    __tablename__ = "disciplines"

    id   = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True, nullable=False, index=True)

    skills = relationship(
        "Skill",
        back_populates="discipline",
        cascade="all, delete",
    )

    items = relationship(
        "Item",
        back_populates="discipline",
        cascade="all, delete",
    )

    def __repr__(self):
        return f"<Discipline(name={self.name})>"


# =============================================================================
# MODEL: Skill (Habilidade curricular)
# =============================================================================

class Skill(Base):
    """
    Habilidade específica vinculada a uma disciplina.

    O campo 'code' segue a codificação da BNCC:
      EM13MAT101 — Ensino Médio, Matemática, habilidade 101
      EF06CI01   — Ensino Fundamental, 6º ano, Ciências, habilidade 01

    Essa codificação é importante para o sistema de blueprint
    (matriz de referência do simulado) e para publicação científica,
    pois permite rastreabilidade pedagógica de cada questão.
    """
    __tablename__ = "skills"

    id          = Column(Integer, primary_key=True)
    code        = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)

    discipline_id = Column(
        Integer,
        ForeignKey("disciplines.id", ondelete="CASCADE"),
        nullable=False,
    )

    discipline = relationship("Discipline", back_populates="skills")
    items      = relationship("Item", back_populates="skill")

    def __repr__(self):
        return f"<Skill(code={self.code})>"


# =============================================================================
# MODEL: Item (Questão do banco de itens)
# =============================================================================

class Item(Base):
    """
    Representa uma questão avaliativa do banco de itens.

    ATENÇÃO: Este model é diferente de Question (app/models/exam.py).

    Item   → questão reutilizável no banco geral
    Question → questão vinculada a um simulado específico

    Campos pedagógicos:
      serie      — ex.: "6º Ano", "1ª Série"
      difficulty — EASY / MEDIUM / HARD
      item_type  — MULTIPLE_CHOICE (padrão) / DISCURSIVE / NUMERIC
      stem       — enunciado da questão
      latex      — indica se o enunciado contém LaTeX
      options_json — alternativas em JSON (para múltipla escolha)
      media_url  — caminho de imagem ou gráfico associado
    """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)

    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,           # questão pode existir sem autor ativo
    )

    discipline_id = Column(
        Integer,
        ForeignKey("disciplines.id", ondelete="CASCADE"),
        nullable=False,
    )

    skill_id = Column(
        Integer,
        ForeignKey("skills.id", ondelete="SET NULL"),
        nullable=True,           # habilidade é opcional (pode ser adicionada depois)
    )

    serie      = Column(String(20), nullable=False, index=True)
    difficulty = Column(Enum(DifficultyEnum), nullable=False)
    item_type  = Column(Enum(ItemTypeEnum), nullable=False)

    stem         = Column(Text, nullable=False)        # enunciado
    options_json = Column(Text, nullable=True)         # alternativas em JSON
    numeric_answer = Column(String(50), nullable=True) # resposta numérica
    media_url    = Column(String(255), nullable=True)  # imagem/gráfico

    # Se True, o enunciado contém LaTeX (ex.: $E=mc^2$)
    # O gerador de PDF trata este campo para renderizar corretamente
    latex = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    owner      = relationship("User", back_populates="items")
    discipline = relationship("Discipline", back_populates="items")
    skill      = relationship("Skill", back_populates="items")

    def __repr__(self):
        return f"<Item(id={self.id}, difficulty={self.difficulty})>"
