# =============================================================================
# app/models/exam.py
# =============================================================================
#
# RESPONSABILIDADE:
#   Define todos os models ORM do modulo de simulados.
#
# O QUE MUDOU NO PASSO 5:
#   ADICIONADOS dois novos models ao final do arquivo:
#     ExamTeacherProgress  -> progresso consolidado por professor/disc/turma
#     ExamProgressLog      -> historico imutavel de eventos (append-only)
#
#   Esses models correspondem as tabelas criadas na migration
#   a1b2c3d4e5f6_teacher_progress.py
#
#   O model Exam recebeu dois novos relacionamentos:
#     .teacher_progress -> lista de ExamTeacherProgress do simulado
#     .progress_log     -> historico de eventos do simulado
#
# ARQUITETURA DO MODULO:
#   Exam                  -> o simulado em si
#   ExamClassAssignment   -> turmas alocadas ao simulado
#   ExamDisciplineQuota   -> cotas por disciplina
#   ExamTeacherAssignment -> atribuicoes professor/disc/turma
#   TeacherClassSubject   -> mapeamento institucional (quem da o que pra quem)
#   Question              -> questoes enviadas pelos professores
#   QuestionOption        -> alternativas de cada questao
#   ExamQuestionLink      -> selecao final de questoes (com ordem e gabarito)
#   ExamTeacherProgress   -> NOVO: progresso consolidado por professor
#   ExamProgressLog       -> NOVO: historico imutavel de eventos
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
# Descoberta dinamica da tabela/PK de Discipline
# Necessario porque o nome da tabela pode variar entre ambientes.
# ---------------------------------------------------------------------------
_DISC_TBL = Discipline.__tablename__
_DISC_PK   = list(Discipline.__table__.primary_key.columns)[0].name
FK_DISCIPLINE = f"{_DISC_TBL}.{_DISC_PK}"


def _disc_pk_attr():
    """Retorna o atributo de PK do model Discipline (ex.: Discipline.id)."""
    return getattr(Discipline, _DISC_PK)


# =============================================================================
# Enums de negocio — Simulado
# =============================================================================

class ExamStatus(str, Enum):
    """
    Ciclo de vida do simulado.

    DRAFT      -> recém criado, ainda sendo configurado
    COLLECTING -> aberto para professores inserirem questoes
    REVIEW     -> coleta encerrada, coordenador revisando
    LOCKED     -> travado, pronto para geracao de PDFs
    GENERATED  -> PDFs gerados e disponiveis
    PUBLISHED  -> distribuido aos alunos
    """
    DRAFT      = "draft"
    COLLECTING = "collecting"
    REVIEW     = "review"
    LOCKED     = "locked"
    GENERATED  = "generated"
    PUBLISHED  = "published"


class AnswerSource(str, Enum):
    """
    Define quem fornece o gabarito das questoes.

    TEACHERS       -> cada professor informa o gabarito ao inserir a questao
    COORDINATOR_OMR -> gabarito definido pelo coordenador via leitura optica
    """
    TEACHERS        = "teachers"
    COORDINATOR_OMR = "coordinator_omr"


class QuestionSource(str, Enum):
    """Origem/formato de inserção da questao."""
    MANUAL = "manual"
    PASTE  = "paste"
    TXT    = "txt"
    DOCX   = "docx"


class QuestionState(str, Enum):
    """Estado de revisao da questao."""
    DRAFT     = "draft"
    SUBMITTED = "submitted"
    APPROVED  = "approved"
    REJECTED  = "rejected"


# =============================================================================
# Enums de negocio — Progresso (NOVOS no Passo 5)
# =============================================================================

class ProgressStatus(str, Enum):
    """
    Status do progresso de um professor em um recorte (exam+disc+turma).

    PENDING  -> nenhuma questao inserida ainda
    PARTIAL  -> pelo menos 1 inserida, mas abaixo da quota
    COMPLETE -> quota atingida ou superada

    Regra de calculo (aplicada pela app ao atualizar ExamTeacherProgress):
        submitted == 0        -> PENDING
        submitted < quota     -> PARTIAL
        submitted >= quota    -> COMPLETE
    """
    PENDING  = "PENDING"
    PARTIAL  = "PARTIAL"
    COMPLETE = "COMPLETE"


class ProgressLogEvent(str, Enum):
    """
    Tipos de evento registrados no historico de progresso.

    QUESTION_ADDED   -> professor inseriu uma questao
    QUESTION_REMOVED -> questao removida (professor ou coordenador)
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

    Um simulado possui:
    - Configuracao: titulo, area, numero de alternativas, fonte do gabarito
    - Turmas alocadas (ExamClassAssignment)
    - Cotas por disciplina (ExamDisciplineQuota)
    - Atribuicoes de professor (ExamTeacherAssignment)
    - Questoes inseridas pelos professores (Question)
    - Selecao final de questoes com ordem e gabarito (ExamQuestionLink)
    - Progresso consolidado por professor (ExamTeacherProgress) [NOVO]
    - Historico de eventos (ExamProgressLog) [NOVO]
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

    created_by = relationship(User)

    # Relacionamentos existentes
    class_assignments   = relationship("ExamClassAssignment",   back_populates="exam", cascade="all, delete-orphan")
    discipline_quotas   = relationship("ExamDisciplineQuota",   back_populates="exam", cascade="all, delete-orphan")
    teacher_assignments = relationship("ExamTeacherAssignment", back_populates="exam", cascade="all, delete-orphan")
    questions           = relationship("Question",              back_populates="exam", cascade="all, delete-orphan")
    selection           = relationship("ExamQuestionLink",      back_populates="exam", cascade="all, delete-orphan")

    # Relacionamentos novos (Passo 5)
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
    exam_id:  Mapped[int] = mapped_column(Integer, ForeignKey("exams.id"),         index=True)
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
    """Quantidade de questoes exigida por disciplina em um simulado."""
    __tablename__ = "exam_discipline_quota"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id:       Mapped[int] = mapped_column(Integer, ForeignKey("exams.id"),      index=True)
    discipline_id: Mapped[int] = mapped_column(Integer, ForeignKey(FK_DISCIPLINE),   index=True)
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
    """Atribuicao de um professor a um recorte (exam + turma + disciplina)."""
    __tablename__ = "exam_teacher_assignment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id:         Mapped[int] = mapped_column(Integer, ForeignKey("exams.id"),         index=True)
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
    """Questao inserida por um professor para um recorte do simulado."""
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id:        Mapped[int] = mapped_column(Integer, ForeignKey("exams.id"),         index=True)
    discipline_id:  Mapped[int] = mapped_column(Integer, ForeignKey(FK_DISCIPLINE),      index=True)
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
    """Alternativa de uma questao (A, B, C, D ou E)."""
    __tablename__ = "question_options"

    id:          Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"), index=True)
    label:       Mapped[str] = mapped_column(String(1), nullable=False)  # 'A'...'E'
    text:        Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint("question_id", "label", name="uq_question_option_label"),
    )

    question = relationship(Question, back_populates="options")


# =============================================================================
# MODEL: ExamQuestionLink
# =============================================================================

class ExamQuestionLink(Base):
    """
    Selecao final de questoes do simulado.
    Cada linha vincula uma questao ao simulado com sua ordem e gabarito.
    """
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
# MODEL: ExamTeacherProgress  [NOVO — Passo 5]
# =============================================================================

class ExamTeacherProgress(Base):
    """
    Progresso consolidado de um professor em um recorte do simulado.

    Um recorte = (simulado, professor, disciplina, turma).

    Exemplo:
        Professor Joao | Matematica | 3aA | Simulado 5
        quota=10 | submitted=7 | status=PARTIAL

    Este registro e atualizado (UPDATE) toda vez que uma questao
    e inserida ou removida por este professor neste recorte.

    O painel do coordenador consulta esta tabela para exibir o
    progresso em tempo real de todos os professores do simulado.

    Relacionado ao log de eventos (ExamProgressLog), que registra
    cada alteracao individualmente para fins de auditoria.
    """
    __tablename__ = "exam_teacher_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Contexto do recorte
    exam_id:         Mapped[int] = mapped_column(Integer, ForeignKey("exams.id",         ondelete="CASCADE"), index=True, nullable=False)
    teacher_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id",         ondelete="CASCADE"), index=True, nullable=False)
    discipline_id:   Mapped[int] = mapped_column(Integer, ForeignKey(FK_DISCIPLINE,       ondelete="CASCADE"), index=True, nullable=False)
    class_id:        Mapped[int] = mapped_column(Integer, ForeignKey("school_classes.id", ondelete="CASCADE"), index=True, nullable=False)

    # Contadores
    quota:     Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    submitted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Status calculado pela aplicacao
    status: Mapped[ProgressStatus] = mapped_column(
        SAEnum(ProgressStatus), nullable=False, default=ProgressStatus.PENDING
    )

    # Timestamp de ultima atualizacao
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "exam_id", "teacher_user_id", "discipline_id", "class_id",
            name="uq_teacher_progress",
        ),
    )

    # Relacionamentos
    exam    = relationship(Exam, back_populates="teacher_progress")
    teacher = relationship(User)
    discipline = relationship(
        Discipline,
        primaryjoin=lambda: ExamTeacherProgress.discipline_id == _disc_pk_attr(),
        foreign_keys=lambda: [ExamTeacherProgress.discipline_id],
    )
    school_class = relationship(SchoolClass)

    def recalculate_status(self) -> None:
        """
        Recalcula e atualiza o status com base nos contadores atuais.
        Deve ser chamado sempre que submitted ou quota for alterado.

        Uso:
            progress.submitted += 1
            progress.recalculate_status()
            db.add(progress)
            db.commit()
        """
        if self.submitted <= 0:
            self.status = ProgressStatus.PENDING
        elif self.submitted < self.quota:
            self.status = ProgressStatus.PARTIAL
        else:
            self.status = ProgressStatus.COMPLETE

        self.last_updated_at = datetime.utcnow()

    def __repr__(self):
        return (
            f"<ExamTeacherProgress("
            f"exam={self.exam_id}, "
            f"teacher={self.teacher_user_id}, "
            f"disc={self.discipline_id}, "
            f"class={self.class_id}, "
            f"{self.submitted}/{self.quota} {self.status})>"
        )


# =============================================================================
# MODEL: ExamProgressLog  [NOVO — Passo 5]
# =============================================================================

class ExamProgressLog(Base):
    """
    Historico IMUTAVEL de eventos de progresso do simulado.

    Cada linha representa um evento discreto no tempo:
      - questao inserida
      - questao removida
      - quota alterada
      - status mudou

    REGRA IMPORTANTE: esta tabela e APPEND-ONLY.
    Nenhuma linha deve ser atualizada ou deletada apos a insercao.
    O historico completo e a fonte de verdade para:
      - Auditoria do processo de construcao do simulado
      - Rastreabilidade metodologica no artigo cientifico
      - Relatorios de desempenho dos professores

    Uso tipico:
        log = ExamProgressLog(
            exam_id=exam.id,
            teacher_user_id=professor.id,
            discipline_id=disc.id,
            class_id=turma.id,
            event_type=ProgressLogEvent.QUESTION_ADDED,
            question_id=questao.id,
            submitted_snap=progresso.submitted,
        )
        db.add(log)
        db.commit()
    """
    __tablename__ = "exam_progress_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Contexto do evento (nullable para preservar historico apos exclusoes)
    exam_id:         Mapped[int]           = mapped_column(Integer, ForeignKey("exams.id",         ondelete="CASCADE"),  nullable=False, index=True)
    teacher_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id",         ondelete="SET NULL"), nullable=True,  index=True)
    discipline_id:   Mapped[Optional[int]] = mapped_column(Integer, ForeignKey(FK_DISCIPLINE,       ondelete="SET NULL"), nullable=True,  index=True)
    class_id:        Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("school_classes.id", ondelete="SET NULL"), nullable=True,  index=True)

    # Tipo do evento
    event_type: Mapped[ProgressLogEvent] = mapped_column(SAEnum(ProgressLogEvent), nullable=False)

    # Questao envolvida (apenas em QUESTION_ADDED / QUESTION_REMOVED)
    question_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("questions.id", ondelete="SET NULL"), nullable=True
    )

    # Snapshots numericos
    quota_before:   Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    quota_after:    Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    submitted_snap: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Anotacao livre
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamp imutavel
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )

    # Relacionamentos (read-only — nunca modificar via cascade)
    exam     = relationship(Exam, back_populates="progress_log")
    teacher  = relationship(User,     foreign_keys=[teacher_user_id])
    question = relationship(Question, foreign_keys=[question_id])

    def __repr__(self):
        return (
            f"<ExamProgressLog("
            f"exam={self.exam_id}, "
            f"event={self.event_type}, "
            f"at={self.occurred_at})>"
        )
