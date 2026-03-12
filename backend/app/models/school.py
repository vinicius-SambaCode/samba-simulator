# -*- coding: utf-8 -*-
"""
Estruturas escolares normalizadas:
- SchoolGrade: representa a SÉRIE/ANO e o NÍVEL (Ensino Fundamental | Ensino Médio).
- ClassSection: representa a TURMA (A, B, C, D, ...).
- SchoolClass: composição de (grade + section) => ex.: 3º + A => "3ºA".
- Student: aluno, indexado por RA e pertencendo a uma SchoolClass.

Obs.: Mantemos UniqueConstraints para evitar duplicatas e facilitar o front.
"""

from enum import Enum

from sqlalchemy import (
    Integer, String, ForeignKey, UniqueConstraint, Enum as SAEnum, Index
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.models.base_models import Base
# ClassDiscipline usa FK para disciplines — importado via string para evitar circular
# relationship("Discipline") usa lazy string ref, não precisa de import direto


class EducationLevel(str, Enum):
    FUNDAMENTAL = "fundamental"  # 6º,7º,8º,9º (p.ex.)
    MEDIO = "medio"              # 1ª,2ª,3ª


class SchoolGrade(Base):
    """
    Série/Ano + Nível. Exs:
      - (FUNDAMENTAL, 6)  -> label: "6º"
      - (MEDIO, 3)        -> label: "3ª"
    year_number: inteiro para ordenação (6,7,8,9,1,2,3)
    label: texto que aparece (ex.: "6º" para fundamental; "3ª" para médio)
    """
    __tablename__ = "school_grades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    level: Mapped[EducationLevel] = mapped_column(SAEnum(EducationLevel), nullable=False, index=True)
    year_number: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str] = mapped_column(String(16), nullable=False)

    __table_args__ = (
        UniqueConstraint("level", "year_number", name="uq_grade_level_year"),
    )


class ClassSection(Base):
    """
    TURMA (A, B, C, D, ...)
    """
    __tablename__ = "class_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    label: Mapped[str] = mapped_column(String(8), nullable=False, unique=True, index=True)  # "A", "B", ...


class SchoolClass(Base):
    """
    Classe (Turma específica) = Grade + Section
    Ex.: (MEDIO, 3) + "A" => "3ªA"
    name é armazenado para facilitar listagens; composto por convenção.
    """
    __tablename__ = "school_classes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    grade_id: Mapped[int] = mapped_column(Integer, ForeignKey("school_grades.id"), nullable=False, index=True)
    section_id: Mapped[int] = mapped_column(Integer, ForeignKey("class_sections.id"), nullable=False, index=True)

    # nome “pronto” para front (ex.: "3ºA" ou "3ªA") — você pode recompor se preferir
    name: Mapped[str] = mapped_column(String(32), nullable=False)

    grade = relationship(SchoolGrade)
    section = relationship(ClassSection)

    __table_args__ = (
        UniqueConstraint("grade_id", "section_id", name="uq_class_grade_section"),
        Index("ix_class_name", "name"),
    )


class Student(Base):
    """
    Alunos com RA único, vinculados a uma SchoolClass.
    """
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ra: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("school_classes.id"), index=True)

    school_class = relationship(SchoolClass)


class ClassDiscipline(Base):
    """
    Grade curricular formal de uma turma.
    Define quais disciplinas compõem o currículo de cada SchoolClass.
    Ex.: Turma 3ªA (Exatas) tem Programação; Turma 3ªB (Humanas) não tem.
    """
    __tablename__ = "class_disciplines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    class_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("school_classes.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    discipline_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("disciplines.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    school_class = relationship("SchoolClass", backref="class_disciplines")
    discipline   = relationship("Discipline")

    __table_args__ = (
        UniqueConstraint("class_id", "discipline_id", name="uq_class_discipline"),
    )
