# =============================================================================
# app/models/exam.py
# =============================================================================
#
# HISTÓRICO DE MUDANÇAS:
#   Passo 5:  ExamTeacherProgress e ExamProgressLog
#   Passo 6:  campos OMR no Exam; String em vez de ENUM PostgreSQL
#   Passo 12: QuestionImage + relacionamento images em Question
#
# ARQUITETURA DO MÓDULO:
#   Exam                  -> o simulado em si
#   ExamClassAssignment   -> turmas alocadas ao simulado
#   ExamDisciplineQuota   -> cotas por disciplina
#   ExamTeacherAssignment -> atribuições professor/disc/turma
#   TeacherClassSubject   -> mapeamento institucional
#   Question              -> questões enviadas pelos professores
#   QuestionOption        -> alternativas de cada questão
#   QuestionImage         -> imagens embutidas extraídas do .docx
#   ExamQuestionLink      -> seleção final (com ordem e gabarito)
#   ExamTeacherProgress   -> progresso consolidado por professor
#   ExamProgressLog       -> histórico imutável de eventos
# =============================================================================

from datetime import datetime
from enum import Enum
from typing import Optional

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
    return getattr(Discipline, _DISC_PK)


# =============================================================================
# Enums de negócio — Simulado
# =============================================================================

class ExamStatus(str, Enum):
    DRAFT      = "draft"
    COLLECTING = "collecting"
    REVIEW     = "review"
    LOCKED     = "locked"
    GENERATED  = "generated"
    PUBLISHED  = "published"


class AnswerSource(str, Enum):
    TEACHERS        = "teachers"
    COORDINATOR_OMR = "coordinator_omr"


class QuestionSource(str, Enum):
    MANUAL = "manual"
    PASTE  = "paste"
    TXT    = "txt"
    DOCX   = "docx"
    PDF    = "pdf"


class QuestionState(str, Enum):
    DRAFT     = "draft"
    SUBMITTED = "submitted"
    APPROVED  = "approved"
    REJECTED  = "rejected"


# =============================================================================
# Enums de negócio — Progresso
# =============================================================================

class ProgressStatus(str, Enum):
    PENDING  = "PENDING"
    PARTIAL  = "PARTIAL"
    COMPLETE = "COMPLETE"


class ProgressLogEvent(str, Enum):
    QUESTION_ADDED   = "QUESTION_ADDED"
    QUESTION_REMOVED = "QUESTION_REMOVED"
    QUOTA_CHANGED    = "QUOTA_CHANGED"
    STATUS_CHANGED   = "STATUS_CHANGED"


# =============================================================================
# MODEL: Exam
# =============================================================================

class Exam(Base):
    __tablename__ = "exams"

    id:            Mapped[int]          = mapped_column(Integer, primary_key=True)
    title:         Mapped[str]          = mapped_column(String(160), nullable=False)
    area:          Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    options_count: Mapped[int]          = mapped_column(Integer, nullable=False)
    answer_source: Mapped[AnswerSource] = mapped_column(SAEnum(AnswerSource), nullable=False)
    status:        Mapped[ExamStatus]   = mapped_column(
        SAEnum(ExamStatus), default=ExamStatus.DRAFT, nullable=False
    )

    created_by_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at:         Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Campos OMR (Passo 6)
    omr_rows:          Mapped[int]          = mapped_column(Integer, nullable=False, server_default="10")
    omr_cols:          Mapped[int]          = mapped_column(Integer, nullable=False, server_default="5")
    omr_header_fields: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    barcode_enabled:   Mapped[bool]         = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    created_by = relationship(User)

    class_assignments   = relationship("ExamClassAssignment",   back_populates="exam", cascade="all, delete-orphan")
    discipline_quotas   = relationship("ExamDisciplineQuota",   back_populates="exam", cascade="all, delete-orphan")
    teacher_assignments = relationship("ExamTeacherAssignment", back_populates="exam", cascade="all, delete-orphan")
    questions           = relationship("Question",              back_populates="exam", cascade="all, delete-orphan")
    selection           = relationship("ExamQuestionLink",      back_populates="exam", cascade="all, delete-orphan")
    teacher_progress    = relationship("ExamTeacherProgress",   back_populates="exam", cascade="all, delete-orphan")
    progress_log        = relationship(
        "ExamProgressLog",
        back_populates="exam",
        cascade="all, delete-orphan",
        order_by="ExamProgressLog.occurred_at",
    )


# =============================================================================
# MODEL: ExamClassAssignment
# =============================================================================

class ExamClassAssignment(Base):
    __tablename__ = "exam_class_assignment"

    id:       Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id:  Mapped[int] = mapped_column(Integer, ForeignKey("exams.id"),          index=True)
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("school_classes.id"), index=True)

    __table_args__ = (UniqueConstraint("exam_id", "class_id", name="uq_exam_class"),)

    exam         = relationship(Exam, back_populates="class_assignments")
    school_class = relationship(SchoolClass)


# =============================================================================
# MODEL: ExamDisciplineQuota
# =============================================================================

class ExamDisciplineQuota(Base):
    __tablename__ = "exam_discipline_quota"

    id:            Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id:       Mapped[int] = mapped_column(Integer, ForeignKey("exams.id"),    index=True)
    discipline_id: Mapped[int] = mapped_column(Integer, ForeignKey(FK_DISCIPLINE), index=True)
    quota:         Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint("exam_id", "discipline_id", name="uq_exam_quota"),)

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
    __tablename__ = "exam_teacher_assignment"

    id:              Mapped[int] = mapped_column(Integer, primary_key=True)
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
    __tablename__ = "teacher_class_subject"

    id:              Mapped[int] = mapped_column(Integer, primary_key=True)
    teacher_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"),          index=True)
    class_id:        Mapped[int] = mapped_column(Integer, ForeignKey("school_classes.id"), index=True)
    discipline_id:   Mapped[int] = mapped_column(Integer, ForeignKey(FK_DISCIPLINE),       index=True)

    __table_args__ = (
        UniqueConstraint("teacher_user_id", "class_id", "discipline_id", name="uq_teacher_class_subject"),
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
    __tablename__ = "questions"

    id:             Mapped[int]           = mapped_column(Integer, primary_key=True)
    exam_id:        Mapped[int]           = mapped_column(Integer, ForeignKey("exams.id"),          index=True)
    discipline_id:  Mapped[int]           = mapped_column(Integer, ForeignKey(FK_DISCIPLINE),       index=True)
    class_id:       Mapped[int]           = mapped_column(Integer, ForeignKey("school_classes.id"), index=True)
    author_user_id: Mapped[int]           = mapped_column(Integer, ForeignKey("users.id"),          index=True)
    source:         Mapped[QuestionSource] = mapped_column(SAEnum(QuestionSource), nullable=False)
    state:          Mapped[QuestionState]  = mapped_column(SAEnum(QuestionState), default=QuestionState.DRAFT, nullable=False)
    stem:           Mapped[str]           = mapped_column(Text, nullable=False)
    has_images:     Mapped[bool]          = mapped_column(Boolean, default=False)

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
    # ← PASSO 12: imagens embutidas extraídas do .docx
    images = relationship(
        "QuestionImage",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="QuestionImage.order_idx",
    )


# =============================================================================
# MODEL: QuestionOption
# =============================================================================

class QuestionOption(Base):
    __tablename__ = "question_options"

    id:          Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"), index=True)
    label:       Mapped[str] = mapped_column(String(1), nullable=False)
    text:        Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (UniqueConstraint("question_id", "label", name="uq_question_option_label"),)

    question = relationship(Question, back_populates="options")


# =============================================================================
# MODEL: QuestionImage  [Passo 12]
# =============================================================================

class QuestionImage(Base):
    """
    Imagem extraída de um arquivo .docx e vinculada a uma questão.

    storage_path : caminho relativo a /app/storage/
                   Ex.: questions/42/img_stem_0_a1b2c3d4.png
    context      : onde a imagem aparece
                   'stem'     → no enunciado
                   'option_A' → na alternativa A  ... etc.
    order_idx    : ordem dentro do mesmo context
    mime_type    : image/png | image/jpeg | image/gif | image/webp
    """
    __tablename__ = "question_images"

    id:           Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_id:  Mapped[int]           = mapped_column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    storage_path: Mapped[str]           = mapped_column(String(512), nullable=False)
    mime_type:    Mapped[str]           = mapped_column(String(64),  nullable=False, default="image/png")
    context:      Mapped[str]           = mapped_column(String(16),  nullable=False, default="stem")
    order_idx:    Mapped[int]           = mapped_column(Integer,     nullable=False, default=0)
    width_px:     Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height_px:    Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at:   Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow)

    question = relationship("Question", back_populates="images")

    def url_path(self) -> str:
        return f"/media/{self.storage_path}"

    def absolute_path(self, base: str = "/app/storage") -> str:
        return f"{base}/{self.storage_path}"

    def __repr__(self):
        return f"<QuestionImage(q={self.question_id}, ctx={self.context}, idx={self.order_idx})>"


# =============================================================================
# MODEL: ExamQuestionLink
# =============================================================================

class ExamQuestionLink(Base):
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
    __tablename__ = "exam_teacher_progress"

    id:              Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exam_id:         Mapped[int] = mapped_column(Integer, ForeignKey("exams.id",         ondelete="CASCADE"), index=True, nullable=False)
    teacher_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id",         ondelete="CASCADE"), index=True, nullable=False)
    discipline_id:   Mapped[int] = mapped_column(Integer, ForeignKey(FK_DISCIPLINE,       ondelete="CASCADE"), index=True, nullable=False)
    class_id:        Mapped[int] = mapped_column(Integer, ForeignKey("school_classes.id", ondelete="CASCADE"), index=True, nullable=False)

    quota:     Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    submitted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status:    Mapped[str] = mapped_column(String(20), nullable=False, server_default="PENDING")

    last_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("exam_id", "teacher_user_id", "discipline_id", "class_id", name="uq_teacher_progress"),
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
        if self.submitted <= 0:
            self.status = ProgressStatus.PENDING.value
        elif self.submitted < self.quota:
            self.status = ProgressStatus.PARTIAL.value
        else:
            self.status = ProgressStatus.COMPLETE.value
        self.last_updated_at = datetime.utcnow()

    def __repr__(self):
        return f"<ExamTeacherProgress(exam={self.exam_id}, teacher={self.teacher_user_id}, {self.submitted}/{self.quota} {self.status})>"


# =============================================================================
# MODEL: ExamProgressLog  [Passo 5 — corrigido no Passo 6]
# =============================================================================

class ExamProgressLog(Base):
    __tablename__ = "exam_progress_log"

    id:              Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    exam_id:         Mapped[int]           = mapped_column(Integer, ForeignKey("exams.id",         ondelete="CASCADE"),  nullable=False, index=True)
    teacher_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id",         ondelete="SET NULL"), nullable=True,  index=True)
    discipline_id:   Mapped[Optional[int]] = mapped_column(Integer, ForeignKey(FK_DISCIPLINE,       ondelete="SET NULL"), nullable=True,  index=True)
    class_id:        Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("school_classes.id", ondelete="SET NULL"), nullable=True,  index=True)
    event_type:      Mapped[str]           = mapped_column(String(30), nullable=False)
    question_id:     Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("questions.id", ondelete="SET NULL"), nullable=True)
    quota_before:    Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    quota_after:     Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    submitted_snap:  Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    note:            Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    occurred_at:     Mapped[datetime]      = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    exam     = relationship(Exam, back_populates="progress_log")
    teacher  = relationship(User,     foreign_keys=[teacher_user_id])
    question = relationship(Question, foreign_keys=[question_id])

    def __repr__(self):
        return f"<ExamProgressLog(exam={self.exam_id}, event={self.event_type}, at={self.occurred_at})>"
