# app/models/exam.py
# -*- coding: utf-8 -*-
"""
Módulo de Simulados (Sprint 1) — Modelos ORM
--------------------------------------------
- Exam e estados
- Quotas por disciplina
- Atribuições de professor (exam + turma + disciplina)
- Questões e alternativas
- Seleção final de questões

Atenção: Estruturas escolares estão em app/models/school.py
          Disciplinas estão em app/models/models.py
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Integer, String, Boolean, DateTime, ForeignKey, Text,
    UniqueConstraint, Enum as SAEnum, Index
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.models.base_models import Base, User
from app.models.models import Discipline            # seu modelo de disciplina
from app.models.school import SchoolClass, Student  # estruturas escolares

# ---------------------------------------------------------------------------
# Descobrir dinamicamente a tabela/PK de Discipline
# ---------------------------------------------------------------------------
_DISC_TBL = Discipline.__tablename__                            # ex.: "disciplines" ou "discipline"
_DISC_PK = list(Discipline.__table__.primary_key.columns)[0].name  # nome da PK (geralmente "id")
FK_DISCIPLINE = f"{_DISC_TBL}.{_DISC_PK}"


# =============================================================================
# Enums de negócio
# =============================================================================
class ExamStatus(str, Enum):
    DRAFT = "draft"
    COLLECTING = "collecting"
    REVIEW = "review"
    LOCKED = "locked"
    GENERATED = "generated"
    PUBLISHED = "published"


class AnswerSource(str, Enum):
    TEACHERS = "teachers"
    COORDINATOR_OMR = "coordinator_omr"


class QuestionSource(str, Enum):
    MANUAL = "manual"
    PASTE = "paste"
    TXT = "txt"
    DOCX = "docx"


class QuestionState(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


# Helper para pegar o atributo de PK dinamicamente (ex.: Discipline.id)
def _disc_pk_attr():
    return getattr(Discipline, _DISC_PK)


# =============================================================================
# Exam (simulado) e relacionamentos diretos
# =============================================================================
class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    area: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    options_count: Mapped[int] = mapped_column(Integer, nullable=False)     # 4 ou 5
    answer_source: Mapped[AnswerSource] = mapped_column(SAEnum(AnswerSource), nullable=False)
    status: Mapped[ExamStatus] = mapped_column(SAEnum(ExamStatus), default=ExamStatus.DRAFT, nullable=False)

    created_by_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    created_by = relationship(User)

    class_assignments = relationship("ExamClassAssignment", back_populates="exam", cascade="all, delete-orphan")
    discipline_quotas = relationship("ExamDisciplineQuota", back_populates="exam", cascade="all, delete-orphan")
    teacher_assignments = relationship("ExamTeacherAssignment", back_populates="exam", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="exam", cascade="all, delete-orphan")
    selection = relationship("ExamQuestionLink", back_populates="exam", cascade="all, delete-orphan")


class ExamClassAssignment(Base):
    __tablename__ = "exam_class_assignment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id: Mapped[int] = mapped_column(Integer, ForeignKey("exams.id"), index=True)
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("school_classes.id"), index=True)

    __table_args__ = (
        UniqueConstraint("exam_id", "class_id", name="uq_exam_class"),
    )

    exam = relationship(Exam, back_populates="class_assignments")
    school_class = relationship(SchoolClass)


class ExamDisciplineQuota(Base):
    __tablename__ = "exam_discipline_quota"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id: Mapped[int] = mapped_column(Integer, ForeignKey("exams.id"), index=True)
    discipline_id: Mapped[int] = mapped_column(Integer, ForeignKey(FK_DISCIPLINE), index=True)
    quota: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("exam_id", "discipline_id", name="uq_exam_quota"),
    )

    exam = relationship(Exam, back_populates="discipline_quotas")
    # >>> Explícito: como juntar quota.discipline_id com Discipline.<pk>
    discipline = relationship(
        Discipline,
        primaryjoin=lambda: ExamDisciplineQuota.discipline_id == _disc_pk_attr(),
        foreign_keys=lambda: [ExamDisciplineQuota.discipline_id],
    )


class ExamTeacherAssignment(Base):
    __tablename__ = "exam_teacher_assignment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id: Mapped[int] = mapped_column(Integer, ForeignKey("exams.id"), index=True)
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("school_classes.id"), index=True)
    discipline_id: Mapped[int] = mapped_column(Integer, ForeignKey(FK_DISCIPLINE), index=True)
    teacher_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)

    __table_args__ = (
        UniqueConstraint("exam_id", "class_id", "discipline_id", "teacher_user_id", name="uq_exam_teacher_slot"),
    )

    exam = relationship(Exam, back_populates="teacher_assignments")
    school_class = relationship(SchoolClass)
    teacher = relationship(User)
    # >>> Explícito:
    discipline = relationship(
        Discipline,
        primaryjoin=lambda: ExamTeacherAssignment.discipline_id == _disc_pk_attr(),
        foreign_keys=lambda: [ExamTeacherAssignment.discipline_id],
    )


class TeacherClassSubject(Base):
    """
    Mapeamento institucional: professor ministra disciplina em determinada turma.
    Usado para validar se o professor pode alimentar aquele recorte no exam.
    """
    __tablename__ = "teacher_class_subject"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    teacher_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("school_classes.id"), index=True)
    discipline_id: Mapped[int] = mapped_column(Integer, ForeignKey(FK_DISCIPLINE), index=True)

    __table_args__ = (
        UniqueConstraint("teacher_user_id", "class_id", "discipline_id", name="uq_teacher_class_subject"),
    )

    teacher = relationship(User)
    school_class = relationship(SchoolClass)
    # >>> Explícito:
    discipline = relationship(
        Discipline,
        primaryjoin=lambda: TeacherClassSubject.discipline_id == _disc_pk_attr(),
        foreign_keys=lambda: [TeacherClassSubject.discipline_id],
    )


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id: Mapped[int] = mapped_column(Integer, ForeignKey("exams.id"), index=True)
    discipline_id: Mapped[int] = mapped_column(Integer, ForeignKey(FK_DISCIPLINE), index=True)
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("school_classes.id"), index=True)

    author_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    source: Mapped[QuestionSource] = mapped_column(SAEnum(QuestionSource), nullable=False)
    state: Mapped[QuestionState] = mapped_column(SAEnum(QuestionState), default=QuestionState.DRAFT, nullable=False)

    stem: Mapped[str] = mapped_column(Text, nullable=False)
    has_images: Mapped[bool] = mapped_column(Boolean, default=False)

    exam = relationship(Exam, back_populates="questions")
    school_class = relationship(SchoolClass)
    author = relationship(User)
    # >>> Explícito:
    discipline = relationship(
        Discipline,
        primaryjoin=lambda: Question.discipline_id == _disc_pk_attr(),
        foreign_keys=lambda: [Question.discipline_id],
    )
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")


class QuestionOption(Base):
    __tablename__ = "question_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"), index=True)
    label: Mapped[str] = mapped_column(String(1), nullable=False)  # 'A'...'E'
    text: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint("question_id", "label", name="uq_question_option_label"),
    )

    question = relationship(Question, back_populates="options")


class ExamQuestionLink(Base):
    __tablename__ = "exam_question_link"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id: Mapped[int] = mapped_column(Integer, ForeignKey("exams.id"), index=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"), index=True)
    order_idx: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    correct_label: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)

    __table_args__ = (
        UniqueConstraint("exam_id", "question_id", name="uq_exam_question_once"),
        UniqueConstraint("exam_id", "order_idx", name="uq_exam_order_idx"),
        Index("ix_exam_question_order", "exam_id", "order_idx"),
    )

    exam = relationship(Exam, back_populates="selection")
    question = relationship(Question)