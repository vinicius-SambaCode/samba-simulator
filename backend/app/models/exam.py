# =============================================================================
# app/models/exam.py
# =============================================================================
#
# RESPONSABILIDADE:
#   Define todos os models ORM do módulo de simulados.
#
# HISTÓRICO DE MUDANÇAS:
#
#   Passo 5:
#     - Adicionados ExamTeacherProgress e ExamProgressLog
#     - Adicionados relacionamentos teacher_progress e progress_log em Exam
#
#   Passo 6:
#     - CORREÇÃO: colunas status/event_type de ExamTeacherProgress e
#       ExamProgressLog agora usam String (alinhado com a migration
#       a1b2c3d4e5f6 que criou VARCHAR em vez de ENUM PostgreSQL).
#       O ORM valida os valores via Python Enum — o banco armazena string.
#     - NOVO: campos OMR adicionados ao model Exam:
#         omr_rows          -> linhas da grade de respostas (padrão 10)
#         omr_cols          -> colunas da grade (padrão 5 = A,B,C,D,E)
#         omr_header_fields -> JSON com campos extras do cabeçalho da folha
#         barcode_enabled   -> se True, imprime QR-code/barcode na folha
#
# ARQUITETURA DO MÓDULO:
#   Exam                  -> o simulado em si
#   ExamClassAssignment   -> turmas alocadas ao simulado
#   ExamDisciplineQuota   -> cotas por disciplina
#   ExamTeacherAssignment -> atribuições professor/disc/turma
#   TeacherClassSubject   -> mapeamento institucional
#   Question              -> questões enviadas pelos professores
#   QuestionOption        -> alternativas de cada questão
#   ExamQuestionLink      -> seleção final (com ordem e gabarito)
#   ExamTeacherProgress   -> progresso consolidado por professor
#   ExamProgressLog       -> histórico imutável de eventos
# =============================================================================

from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    Integer, String, Boolean, DateTime, ForeignKey, Text,
    UniqueConstraint, Enum as SAEnum, Index
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.models.base_models import Base, User
from app.models.models import Discipline
from app.models.school import SchoolClass

# ---------------------------------------------------------------------------
# Descoberta dinâmica da tabela/PK de Discipline.
# ---------------------------------------------------------------------------
_DISC_TBL = Discipline.__tablename__
_DISC_PK   = list(Discipline.__table__.primary_key.columns)[0].name
FK_DISCIPLINE = f"{_DISC_TBL}.{_DISC_PK}"


def _disc_pk_attr():
    """Retorna o atributo de PK do model Discipline (ex.: Discipline.id)."""
    return getattr(Discipline, _DISC_PK)


# =============================================================================
# Enums de negócio — Simulado
# =============================================================================

class ExamStatus(str, Enum):
    """
    Ciclo de vida do simulado.

    DRAFT      -> recém criado, ainda sendo configurado
    COLLECTING -> aberto para professores inserirem questões
    REVIEW     -> coleta encerrada, coordenador revisando
    LOCKED     -> travado, pronto para geração de PDFs
    GENERATED  -> PDFs gerados e disponíveis
    PUBLISHED  -> distribuído aos alunos
    """
    DRAFT      = "draft"
    COLLECTING = "collecting"
    REVIEW     = "review"
    LOCKED     = "locked"
    GENERATED  = "generated"
    PUBLISHED  = "published"


class AnswerSource(str, Enum):
    """
    Define quem fornece o gabarito das questões.

    TEACHERS        -> cada professor informa ao inserir a questão
    COORDINATOR_OMR -> gabarito definido pelo coordenador via leitura óptica
    """
    TEACHERS        = "teachers"
    COORDINATOR_OMR = "coordinator_omr"


class QuestionSource(str, Enum):
    """Origem/formato de inserção da questão."""
    MANUAL = "manual"
    PASTE  = "paste"
    TXT    = "txt"
    DOCX   = "docx"


class QuestionState(str, Enum):
    """Estado de revisão da questão."""
    DRAFT     = "draft"
    SUBMITTED = "submitted"
    APPROVED  = "approved"
    REJECTED  = "rejected"


# =============================================================================
# Enums de negócio — Progresso (adicionados no Passo 5)
# =============================================================================

class ProgressStatus(str, Enum):
    """
    Status do progresso de um professor em um recorte (exam+disc+turma).

    PENDING  -> nenhuma questão inserida ainda
    PARTIAL  -> pelo menos 1 inserida, mas abaixo da quota
    COMPLETE -> quota atingida ou superada

    Regra de cálculo (aplicada pela app ao atualizar ExamTeacherProgress):
        submitted == 0        -> PENDING
        0 < submitted < quota -> PARTIAL
        submitted >= quota    -> COMPLETE
    """
    PENDING  = "PENDING"
    PARTIAL  = "PARTIAL"
    COMPLETE = "COMPLETE"


class ProgressLogEvent(str, Enum):
    """
    Tipos de evento registrados no histórico de progresso.

    QUESTION_ADDED   -> professor inseriu uma questão
    QUESTION_REMOVED -> questão removida (professor ou coordenador)
    QUOTA_CHANGED    -> coordenador alterou a quota da disciplina
    STATUS_CHANGED   -> status do progresso mudou
    """
    QUESTION_ADDED   = "QUESTION_ADDED"
    QUESTION_REMOVED = "QUESTION_REMOVED"
    QUOTA_CHANGED    = "QUOTA_CHANGED"
    STATUS_CHANGED   = "STATUS_CHANGED"


# =============================================================================
# MODEL: Exam
# =============================================================================

class Exam(Base):
    """
    Representa um simulado completo.

    Campos de configuração geral:
      title         -> título do simulado
      area          -> área do conhecimento (ex.: "Ciências da Natureza")
      options_count -> número de alternativas por questão (4 ou 5)
      answer_source -> quem define o gabarito (professores ou OMR)
      status        -> ciclo de vida do simulado

    Campos OMR (NOVOS no Passo 6):
      omr_rows          -> número de linhas da grade de respostas
                           Exemplo: 20 questões = 20 linhas
      omr_cols          -> número de colunas (= número de alternativas)
                           Padrão: 5 (A, B, C, D, E). Use 4 para A-D.
      omr_header_fields -> JSON com campos extras do cabeçalho da folha
                           Exemplo: '["nome", "turma", "data"]'
                           O gerador de PDF usa este campo para renderizar
                           o cabeçalho personalizado de cada escola.
      barcode_enabled   -> se True, imprime QR-code ou código de barras
                           na folha para identificação automática na leitura

    Relacionamentos:
      class_assignments   -> turmas alocadas
      discipline_quotas   -> cotas por disciplina
      teacher_assignments -> atribuições de professores
      questions           -> questões inseridas
      selection           -> seleção final com ordem e gabarito
      teacher_progress    -> progresso consolidado por professor
      progress_log        -> histórico de eventos (append-only)
    """
    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    area: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    options_count: Mapped[int] = mapped_column(Integer, nullable=False)
    answer_source: Mapped[AnswerSource] = mapped_column(SAEnum(AnswerSource), nullable=False)
    status: Mapped[ExamStatus] = mapped_column(
        SAEnum(ExamStatus), default=ExamStatus.DRAFT, nullable=False
    )

    created_by_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # -------------------------------------------------------------------------
    # Campos OMR — adicionados no Passo 6
    # -------------------------------------------------------------------------

    # Linhas da grade = número máximo de questões na folha (padrão: 10)
    omr_rows: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="10"
    )

    # Colunas da grade = número de alternativas (padrão: 5 → A,B,C,D,E)
    omr_cols: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="5"
    )

    # Campos do cabeçalho em JSON. Ex.: '["nome", "turma", "numero"]'
    # Se None, o gerador de PDF usa o cabeçalho padrão da escola.
    omr_header_fields: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )

    # Se True, a folha terá QR-code/barcode para identificação automática
    barcode_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )

    # -------------------------------------------------------------------------
    created_by = relationship(User)

    class_assignments   = relationship("ExamClassAssignment",   back_populates="exam", cascade="all, delete-orphan")
    discipline_quotas   = relationship("ExamDisciplineQuota",   back_populates="exam", cascade="all, delete-orphan")
    teacher_assignments = relationship("ExamTeacherAssignment", back_populates="exam", cascade="all, delete-orphan")
    questions           = relationship("Question",              back_populates="exam", cascade="all, delete-orphan")
    selection           = relationship("ExamQuestionLink",      back_populates="exam", cascade="all, delete-orphan")

    teacher_progress = relationship(
        "ExamTeacherProgress",
        back_populates="exam",
        cascade="all, delete-orphan",
    )
    progress_log = relationship(
        "ExamProgressLog",
        back_populates="exam",
        cascade="all, delete-orphan",
        order_by="ExamProgressLog.occurred_at",
    )


# =============================================================================
# MODEL: ExamClassAssignment
# =============================================================================

class ExamClassAssignment(Base):
    """Turmas alocadas a um simulado."""
    __tablename__ = "exam_class_assignment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id:  Mapped[int] = mapped_column(Integer, ForeignKey("exams.id"),          index=True)
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("school_classes.id"), index=True)

    __table_args__ = (
        UniqueConstraint("exam_id", "class_id", name="uq_exam_class"),
    )

    exam         = relationship(Exam, back_populates="class_assignments")
    school_class = relationship(SchoolClass)


# =============================================================================
# MODEL: ExamDisciplineQuota
# =============================================================================

class ExamDisciplineQuota(Base):
    """Quantidade de questões exigida por disciplina em um simulado."""
    __tablename__ = "exam_discipline_quota"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id:       Mapped[int] = mapped_column(Integer, ForeignKey("exams.id"),    index=True)
    discipline_id: Mapped[int] = mapped_column(Integer, ForeignKey(FK_DISCIPLINE), index=True)
    quota:         Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("exam_id", "discipline_id", name="uq_exam_quota"),
    )

    exam = relationship(Exam, back_populates="discipline_quotas")
    discipline = relationship(
        Discipline,
        primaryjoin=lambda: ExamDisciplineQuota.discipline_id == _disc_pk_attr(),
        foreign_keys=lambda: [ExamDisciplineQuota.discipline_id],
    )


# =============================================================================
# MODEL: ExamTeacherAssignment
# =============================================================================

class ExamTeacherAssignment(Base):
    """Atribuição de um professor a um recorte (exam + turma + disciplina)."""
    __tablename__ = "exam_teacher_assignment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id:         Mapped[int] = mapped_column(Integer, ForeignKey("exams.id"),          index=True)
    class_id:        Mapped[int] = mapped_column(Integer, ForeignKey("school_classes.id"), index=True)
    discipline_id:   Mapped[int] = mapped_column(Integer, ForeignKey(FK_DISCIPLINE),       index=True)
    teacher_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"),          index=True)

    __table_args__ = (
        UniqueConstraint(
            "exam_id", "class_id", "discipline_id", "teacher_user_id",
            name="uq_exam_teacher_slot",
        ),
    )

    exam         = relationship(Exam, back_populates="teacher_assignments")
    school_class = relationship(SchoolClass)
    teacher      = relationship(User)
    discipline   = relationship(
        Discipline,
        primaryjoin=lambda: ExamTeacherAssignment.discipline_id == _disc_pk_attr(),
        foreign_keys=lambda: [ExamTeacherAssignment.discipline_id],
    )


# =============================================================================
# MODEL: TeacherClassSubject
# =============================================================================

class TeacherClassSubject(Base):
    """
    Mapeamento institucional: professor ministra disciplina em determinada turma.
    Usado para validar se o professor pode alimentar aquele recorte no simulado.
    """
    __tablename__ = "teacher_class_subject"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    teacher_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"),          index=True)
    class_id:        Mapped[int] = mapped_column(Integer, ForeignKey("school_classes.id"), index=True)
    discipline_id:   Mapped[int] = mapped_column(Integer, ForeignKey(FK_DISCIPLINE),       index=True)

    __table_args__ = (
        UniqueConstraint(
            "teacher_user_id", "class_id", "discipline_id",
            name="uq_teacher_class_subject",
        ),
    )

    teacher      = relationship(User)
    school_class = relationship(SchoolClass)
    discipline   = relationship(
        Discipline,
        primaryjoin=lambda: TeacherClassSubject.discipline_id == _disc_pk_attr(),
        foreign_keys=lambda: [TeacherClassSubject.discipline_id],
    )


# =============================================================================
# MODEL: Question
# =============================================================================

class Question(Base):
    """Questão inserida por um professor para um recorte do simulado."""
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id:        Mapped[int] = mapped_column(Integer, ForeignKey("exams.id"),          index=True)
    discipline_id:  Mapped[int] = mapped_column(Integer, ForeignKey(FK_DISCIPLINE),       index=True)
    class_id:       Mapped[int] = mapped_column(Integer, ForeignKey("school_classes.id"), index=True)
    author_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"),          index=True)

    source: Mapped[QuestionSource] = mapped_column(SAEnum(QuestionSource), nullable=False)
    state:  Mapped[QuestionState]  = mapped_column(
        SAEnum(QuestionState), default=QuestionState.DRAFT, nullable=False
    )

    stem:       Mapped[str]  = mapped_column(Text, nullable=False)
    has_images: Mapped[bool] = mapped_column(Boolean, default=False)

    exam         = relationship(Exam, back_populates="questions")
    school_class = relationship(SchoolClass)
    author       = relationship(User)
    discipline   = relationship(
        Discipline,
        primaryjoin=lambda: Question.discipline_id == _disc_pk_attr(),
        foreign_keys=lambda: [Question.discipline_id],
    )
    options = relationship(
        "QuestionOption", back_populates="question", cascade="all, delete-orphan"
    )


# =============================================================================
# MODEL: QuestionOption
# =============================================================================

class QuestionOption(Base):
    """Alternativa de uma questão (A, B, C, D ou E)."""
    __tablename__ = "question_options"

    id:          Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"), index=True)
    label:       Mapped[str] = mapped_column(String(1), nullable=False)
    text:        Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint("question_id", "label", name="uq_question_option_label"),
    )

    question = relationship(Question, back_populates="options")


# =============================================================================
# MODEL: ExamQuestionLink
# =============================================================================

class ExamQuestionLink(Base):
    """Seleção final de questões do simulado com ordem e gabarito."""
    __tablename__ = "exam_question_link"

    id:            Mapped[int]           = mapped_column(Integer, primary_key=True)
    exam_id:       Mapped[int]           = mapped_column(Integer, ForeignKey("exams.id"),     index=True)
    question_id:   Mapped[int]           = mapped_column(Integer, ForeignKey("questions.id"), index=True)
    order_idx:     Mapped[int]           = mapped_column(Integer, nullable=False, default=0)
    correct_label: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)

    __table_args__ = (
        UniqueConstraint("exam_id", "question_id", name="uq_exam_question_once"),
        UniqueConstraint("exam_id", "order_idx",   name="uq_exam_order_idx"),
        Index("ix_exam_question_order", "exam_id", "order_idx"),
    )

    exam     = relationship(Exam, back_populates="selection")
    question = relationship(Question)


# =============================================================================
# MODEL: ExamTeacherProgress  [Passo 5 — corrigido no Passo 6]
# =============================================================================

class ExamTeacherProgress(Base):
    """
    Progresso consolidado de um professor em um recorte do simulado.

    Um recorte = (simulado, professor, disciplina, turma).

    IMPORTANTE sobre a coluna `status`:
        Armazenada como VARCHAR(20) no banco (não como ENUM PostgreSQL).
        Valores válidos definidos pelo Python Enum ProgressStatus:
            "PENDING" | "PARTIAL" | "COMPLETE"
        A validação ocorre na camada Python, não no banco.

    Atualizado (UPDATE) toda vez que uma questão é inserida ou removida.
    """
    __tablename__ = "exam_teacher_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    exam_id:         Mapped[int] = mapped_column(Integer, ForeignKey("exams.id",         ondelete="CASCADE"), index=True, nullable=False)
    teacher_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id",         ondelete="CASCADE"), index=True, nullable=False)
    discipline_id:   Mapped[int] = mapped_column(Integer, ForeignKey(FK_DISCIPLINE,       ondelete="CASCADE"), index=True, nullable=False)
    class_id:        Mapped[int] = mapped_column(Integer, ForeignKey("school_classes.id", ondelete="CASCADE"), index=True, nullable=False)

    quota:     Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    submitted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # VARCHAR — alinhado com migration a1b2c3d4e5f6
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="PENDING")

    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "exam_id", "teacher_user_id", "discipline_id", "class_id",
            name="uq_teacher_progress",
        ),
    )

    exam         = relationship(Exam, back_populates="teacher_progress")
    teacher      = relationship(User)
    school_class = relationship(SchoolClass)
    discipline   = relationship(
        Discipline,
        primaryjoin=lambda: ExamTeacherProgress.discipline_id == _disc_pk_attr(),
        foreign_keys=lambda: [ExamTeacherProgress.discipline_id],
    )

    def recalculate_status(self) -> None:
        """
        Recalcula status com base nos contadores.
        Chame sempre que submitted ou quota for alterado.

        Uso:
            progress.submitted += 1
            progress.recalculate_status()
            db.add(progress)
            db.commit()
        """
        if self.submitted <= 0:
            self.status = ProgressStatus.PENDING.value
        elif self.submitted < self.quota:
            self.status = ProgressStatus.PARTIAL.value
        else:
            self.status = ProgressStatus.COMPLETE.value
        self.last_updated_at = datetime.utcnow()

    def __repr__(self):
        return (
            f"<ExamTeacherProgress(exam={self.exam_id}, "
            f"teacher={self.teacher_user_id}, "
            f"{self.submitted}/{self.quota} {self.status})>"
        )


# =============================================================================
# MODEL: ExamProgressLog  [Passo 5 — corrigido no Passo 6]
# =============================================================================

class ExamProgressLog(Base):
    """
    Histórico IMUTÁVEL de eventos de progresso. APPEND-ONLY.

    IMPORTANTE sobre a coluna `event_type`:
        Armazenada como VARCHAR(30) no banco (não como ENUM PostgreSQL).
        Valores válidos definidos pelo Python Enum ProgressLogEvent.

    Uso:
        log = ExamProgressLog(
            exam_id=exam.id,
            teacher_user_id=professor.id,
            discipline_id=disc.id,
            class_id=turma.id,
            event_type=ProgressLogEvent.QUESTION_ADDED.value,
            question_id=questao.id,
            submitted_snap=progresso.submitted,
        )
        db.add(log)
        db.commit()
    """
    __tablename__ = "exam_progress_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    exam_id:         Mapped[int]           = mapped_column(Integer, ForeignKey("exams.id",         ondelete="CASCADE"),  nullable=False, index=True)
    teacher_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id",         ondelete="SET NULL"), nullable=True,  index=True)
    discipline_id:   Mapped[Optional[int]] = mapped_column(Integer, ForeignKey(FK_DISCIPLINE,       ondelete="SET NULL"), nullable=True,  index=True)
    class_id:        Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("school_classes.id", ondelete="SET NULL"), nullable=True,  index=True)

    # VARCHAR — alinhado com migration a1b2c3d4e5f6
    event_type: Mapped[str] = mapped_column(String(30), nullable=False)

    question_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("questions.id", ondelete="SET NULL"), nullable=True
    )

    quota_before:   Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    quota_after:    Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    submitted_snap: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    note:           Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )

    exam     = relationship(Exam, back_populates="progress_log")
    teacher  = relationship(User,     foreign_keys=[teacher_user_id])
    question = relationship(Question, foreign_keys=[question_id])

    def __repr__(self):
        return (
            f"<ExamProgressLog(exam={self.exam_id}, "
            f"event={self.event_type}, at={self.occurred_at})>"
        )
