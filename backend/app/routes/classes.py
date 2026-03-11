from sqlalchemy.orm import Session, joinedload
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user
from app.core.deps import require_role
from app.models.base_models import User
from app.models.school import SchoolGrade, ClassSection, SchoolClass
from app.models.models import Discipline
from app.models.exam import TeacherClassSubject
from app.schemas.school import (
    GradeCreate, GradeOut, SectionCreate, SectionOut, ClassCreate, ClassOut
)

router = APIRouter(prefix="/school", tags=["school"])


# ------------ Grades ------------
@router.post("/grades", response_model=GradeOut, dependencies=[Depends(require_role("COORDINATOR"))])
def create_grade(data: GradeCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    exists = db.query(SchoolGrade).filter(
        SchoolGrade.level == data.level,
        SchoolGrade.year_number == data.year_number
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="Já existe esta série/ano neste nível.")
    grade = SchoolGrade(level=data.level, year_number=data.year_number, label=data.label)
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade


@router.get("/grades", response_model=list[GradeOut])
def list_grades(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(SchoolGrade).order_by(SchoolGrade.level, SchoolGrade.year_number).all()


# ------------ Sections ------------
@router.post("/sections", response_model=SectionOut, dependencies=[Depends(require_role("COORDINATOR"))])
def create_section(data: SectionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    label = data.label.strip().upper()
    exists = db.query(ClassSection).filter(ClassSection.label == label).first()
    if exists:
        raise HTTPException(status_code=400, detail="Já existe esta turma/section.")
    sec = ClassSection(label=label)
    db.add(sec)
    db.commit()
    db.refresh(sec)
    return sec


@router.get("/sections", response_model=list[SectionOut])
def list_sections(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(ClassSection).order_by(ClassSection.label).all()


# ------------ Classes ------------
@router.post("/classes", response_model=ClassOut, dependencies=[Depends(require_role("COORDINATOR"))])
def create_class(data: ClassCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    grade = db.get(SchoolGrade, data.grade_id)
    sec = db.get(ClassSection, data.section_id)
    if not grade or not sec:
        raise HTTPException(status_code=400, detail="grade_id ou section_id inválidos.")
    name = f"{grade.label}{sec.label}"
    exists = db.query(SchoolClass).filter(
        SchoolClass.grade_id == grade.id,
        SchoolClass.section_id == sec.id
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="Esta classe (série+turma) já existe.")
    sc = SchoolClass(grade_id=grade.id, section_id=sec.id, name=name)
    db.add(sc)
    db.commit()
    db.refresh(sc)
    return sc


@router.get("/classes", response_model=list[ClassOut])
def list_classes(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(SchoolClass).options(
        joinedload(SchoolClass.grade)
    ).order_by(SchoolClass.name).all()


@router.delete("/classes/{class_id}", status_code=204, dependencies=[Depends(require_role("COORDINATOR"))])
def delete_class(class_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sc = db.get(SchoolClass, class_id)
    if not sc:
        raise HTTPException(status_code=404, detail="Turma não encontrada.")
    db.delete(sc)
    db.commit()
    return None


@router.get("/teachers", dependencies=[Depends(require_role("COORDINATOR", "ADMIN"))])
def list_teachers(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from app.models.base_models import Role, user_roles
    teachers = (
        db.query(User)
        .join(user_roles, user_roles.c.user_id == User.id)
        .join(Role, Role.id == user_roles.c.role_id)
        .filter(Role.name == "TEACHER")
        .order_by(User.name)
        .all()
    )
    return [{"id": t.id, "name": t.name, "email": t.email} for t in teachers]


# ------------ TeacherClassSubject ------------

@router.get("/my-subjects")
def list_my_subjects(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Retorna os vínculos de turma+disciplina do professor logado."""
    rows = db.query(TeacherClassSubject).filter(
        TeacherClassSubject.teacher_user_id == user.id
    ).all()
    result = []
    for r in rows:
        cls  = db.get(SchoolClass, r.class_id)
        disc = db.get(Discipline,  r.discipline_id)
        result.append({
            "id":              r.id,
            "class_id":        r.class_id,
            "class_name":      cls.name  if cls  else f"Turma #{r.class_id}",
            "discipline_id":   r.discipline_id,
            "discipline_name": disc.name if disc else f"Disc. #{r.discipline_id}",
        })
    return result


@router.get("/teacher-subjects", dependencies=[Depends(require_role("COORDINATOR", "ADMIN"))])
def list_teacher_subjects(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(TeacherClassSubject).all()
    return [
        {
            "id": r.id,
            "teacher_user_id": r.teacher_user_id,
            "class_id": r.class_id,
            "discipline_id": r.discipline_id,
        }
        for r in rows
    ]


@router.post("/teacher-subjects", dependencies=[Depends(require_role("COORDINATOR", "ADMIN"))])
def create_teacher_subject(
    data: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    exists = db.query(TeacherClassSubject).filter_by(
        teacher_user_id=data["teacher_user_id"],
        class_id=data["class_id"],
        discipline_id=data["discipline_id"],
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="Vínculo já existe.")
    link = TeacherClassSubject(
        teacher_user_id=data["teacher_user_id"],
        class_id=data["class_id"],
        discipline_id=data["discipline_id"],
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return {
        "id": link.id,
        "teacher_user_id": link.teacher_user_id,
        "class_id": link.class_id,
        "discipline_id": link.discipline_id,
    }


@router.delete("/teacher-subjects/{link_id}", dependencies=[Depends(require_role("COORDINATOR", "ADMIN"))])
def delete_teacher_subject(
    link_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    link = db.get(TeacherClassSubject, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Vínculo não encontrado.")
    db.delete(link)
    db.commit()
    return {"detail": "Vínculo removido."}