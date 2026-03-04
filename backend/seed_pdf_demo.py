# backend/scripts/seed_pdf_demo.py
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from app.core.db import SessionLocal
from app.models.exam import Exam, ExamStatus  # sua model real
from app.models.school import (
    SchoolGrade, ClassSection, SchoolClass, Student, EducationLevel
)
from app.models.models import User  # ajuste se User estiver em outro módulo

def pick_enum_default(sa_enum_type) -> Any:
    """
    Retorna um valor válido para uma coluna Enum do SQLAlchemy.
    - Se for Enum de strings: pega o primeiro item de .enums
    - Se for Python Enum: pega o primeiro membro (enum_class)
    - Fallback: string 'DEFAULT'
    """
    # Enum de strings declarada como SAEnum("A", "B", ...)
    if hasattr(sa_enum_type, "enums") and sa_enum_type.enums:
        return sa_enum_type.enums[0]

    # Enum Python declarada como SAEnum(EnumClass)
    if hasattr(sa_enum_type, "enum_class") and sa_enum_type.enum_class is not None:
        enum_cls = sa_enum_type.enum_class
        try:
            return list(enum_cls)[0]  # retorna o membro Enum (não o .value)
        except Exception:
            # fallback para o primeiro .value se existir
            try:
                return list(map(lambda m: m.value, enum_cls))[0]
            except Exception:
                pass

    # Fallback genérico
    return "DEFAULT"

def seed_exam_locked(s) -> Exam:
    """
    Garante Exam(id=1) em LOCKED preenchendo todas as colunas NOT NULL com defaults válidos.
    """
    exam = s.get(Exam, 1)
    cols = Exam.__table__.c  # colunas mapeadas
    need_insert = False

    if not exam:
        need_insert = True
        exam = Exam(id=1)

    changed = False

    # title
    if getattr(exam, "title", None) in (None, "") and not cols.title.nullable:
        setattr(exam, "title", "Demo Exam"); changed = True

    # status
    if getattr(exam, "status", None) != ExamStatus.LOCKED:
        setattr(exam, "status", ExamStatus.LOCKED); changed = True

    # options_count
    if "options_count" in cols and not cols.options_count.nullable:
        if getattr(exam, "options_count", None) in (None, 0):
            setattr(exam, "options_count", 4); changed = True

    # area (se NOT NULL e Enum)
    if "area" in cols and not cols.area.nullable:
        if getattr(exam, "area", None) is None:
            setattr(exam, "area", pick_enum_default(cols.area.type)); changed = True

    # answer_source (se NOT NULL e Enum)
    if "answer_source" in cols and not cols.answer_source.nullable:
        if getattr(exam, "answer_source", None) is None:
            setattr(exam, "answer_source", pick_enum_default(cols.answer_source.type)); changed = True

    # created_by_user_id (se NOT NULL)
    if "created_by_user_id" in cols and not cols.created_by_user_id.nullable:
        if getattr(exam, "created_by_user_id", None) is None:
            admin = s.query(User).filter(User.email == "admin@samba.local").first()
            setattr(exam, "created_by_user_id", getattr(admin, "id", 1)); changed = True

    # created_at (se NOT NULL)
    if "created_at" in cols and not cols.created_at.nullable:
        if getattr(exam, "created_at", None) is None:
            setattr(exam, "created_at", datetime.utcnow()); changed = True

    if need_insert:
        s.add(exam)
    if changed or need_insert:
        s.commit(); s.refresh(exam)

    print(
        "Exam pronto:",
        exam.id,
        getattr(exam, "status", None),
        "options_count=", getattr(exam, "options_count", None),
        "area=", getattr(exam, "area", None),
        "answer_source=", getattr(exam, "answer_source", None),
        "created_by_user_id=", getattr(exam, "created_by_user_id", None),
    )
    return exam

def seed_school_minimal(s):
    """
    Garante SchoolGrade(1)->'9º', ClassSection(1)->'A', SchoolClass(10)->'9ºA', Student(100)->'RA100'.
    """
    grade = s.get(SchoolGrade, 1)
    if not grade:
        grade = SchoolGrade(id=1, level=EducationLevel.FUNDAMENTAL, year_number=9, label="9º")
        s.add(grade); s.commit(); s.refresh(grade)

    section = s.get(ClassSection, 1)
    if not section:
        section = ClassSection(id=1, label="A")
        s.add(section); s.commit(); s.refresh(section)

    clazz = s.get(SchoolClass, 10)
    if not clazz:
        clazz = SchoolClass(id=10, grade_id=grade.id, section_id=section.id, name=f"{grade.label}{section.label}")
        s.add(clazz); s.commit(); s.refresh(clazz)

    stu = s.get(Student, 100)
    if not stu:
        stu = Student(id=100, ra="RA100", name="Demo Student 100", class_id=clazz.id)
        s.add(stu); s.commit(); s.refresh(stu)

    print(
        "Class pronta:", clazz.id, "->", clazz.name,
        "(grade_id, section_id)=", clazz.grade_id, clazz.section_id
    )
    print("Student pronto:", stu.id, stu.ra, "class_id=", stu.class_id)

def main():
    s = SessionLocal()
    try:
        seed_exam_locked(s)
        seed_school_minimal(s)
        print("DONE")
    finally:
        s.close()

if __name__ == "__main__":
    main()
