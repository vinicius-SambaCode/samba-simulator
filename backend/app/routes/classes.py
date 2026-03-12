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


# ------------ Class Disciplines (grade curricular) --------------------------

@router.get("/classes/{class_id}/disciplines", dependencies=[Depends(require_role("COORDINATOR", "ADMIN", "TEACHER"))])
def list_class_disciplines(class_id: int, db: Session = Depends(get_db)):
    """Lista as disciplinas vinculadas a uma turma (grade curricular)."""
    from sqlalchemy import text
    rows = db.execute(
        text("SELECT id, class_id, discipline_id FROM class_disciplines WHERE class_id = :cid ORDER BY id"),
        {"cid": class_id}
    ).fetchall()
    result = []
    for row in rows:
        disc = db.get(Discipline, row.discipline_id)
        result.append({
            "id": row.id,
            "class_id": row.class_id,
            "discipline_id": row.discipline_id,
            "discipline_name": disc.name if disc else f"Disc #{row.discipline_id}",
        })
    return result


@router.post("/classes/{class_id}/disciplines", dependencies=[Depends(require_role("COORDINATOR", "ADMIN"))])
def add_class_discipline(class_id: int, data: dict, db: Session = Depends(get_db)):
    """Vincula uma disciplina a uma turma."""
    from sqlalchemy import text
    disc_id = data.get("discipline_id")
    if not disc_id:
        raise HTTPException(400, "discipline_id é obrigatório.")
    # Verificar se já existe
    existing = db.execute(
        text("SELECT id FROM class_disciplines WHERE class_id = :cid AND discipline_id = :did"),
        {"cid": class_id, "did": disc_id}
    ).fetchone()
    if existing:
        raise HTTPException(400, "Disciplina já vinculada a esta turma.")
    result = db.execute(
        text("INSERT INTO class_disciplines (class_id, discipline_id) VALUES (:cid, :did) RETURNING id"),
        {"cid": class_id, "did": disc_id}
    )
    db.commit()
    new_id = result.fetchone()[0]
    disc = db.get(Discipline, disc_id)
    return {
        "id": new_id,
        "class_id": class_id,
        "discipline_id": disc_id,
        "discipline_name": disc.name if disc else f"Disc #{disc_id}",
    }


@router.delete("/classes/{class_id}/disciplines/{disc_id}", status_code=204, dependencies=[Depends(require_role("COORDINATOR", "ADMIN"))])
def remove_class_discipline(class_id: int, disc_id: int, db: Session = Depends(get_db)):
    """Remove vínculo de disciplina de uma turma."""
    from sqlalchemy import text
    db.execute(
        text("DELETE FROM class_disciplines WHERE class_id = :cid AND discipline_id = :did"),
        {"cid": class_id, "did": disc_id}
    )
    db.commit()
    return None


@router.post("/classes/{class_id}/clone-disciplines", dependencies=[Depends(require_role("COORDINATOR", "ADMIN"))])
def clone_disciplines(class_id: int, data: dict, db: Session = Depends(get_db)):
    """
    Clona todas as disciplinas de uma turma de origem para uma ou mais turmas de destino.
    Body: { "source_class_id": int, "target_class_ids": [int, ...], "overwrite": bool }
    """
    from sqlalchemy import text

    source_id = data.get("source_class_id")
    target_ids = data.get("target_class_ids", [])
    overwrite = data.get("overwrite", False)

    if not source_id:
        raise HTTPException(400, "source_class_id é obrigatório.")
    if not target_ids:
        raise HTTPException(400, "target_class_ids não pode ser vazio.")

    # Buscar disciplinas da turma origem
    source_rows = db.execute(
        text("SELECT discipline_id FROM class_disciplines WHERE class_id = :cid"),
        {"cid": source_id}
    ).fetchall()
    disc_ids = [r.discipline_id for r in source_rows]

    if not disc_ids:
        raise HTTPException(400, "A turma de origem não tem disciplinas vinculadas.")

    summary = {}
    for target_id in target_ids:
        if target_id == source_id:
            continue
        added = 0
        skipped = 0
        if overwrite:
            # Remove todos os vínculos existentes antes de clonar
            db.execute(
                text("DELETE FROM class_disciplines WHERE class_id = :cid"),
                {"cid": target_id}
            )
        for disc_id in disc_ids:
            existing = db.execute(
                text("SELECT id FROM class_disciplines WHERE class_id = :cid AND discipline_id = :did"),
                {"cid": target_id, "did": disc_id}
            ).fetchone()
            if existing:
                skipped += 1
            else:
                db.execute(
                    text("INSERT INTO class_disciplines (class_id, discipline_id) VALUES (:cid, :did)"),
                    {"cid": target_id, "did": disc_id}
                )
                added += 1
        summary[target_id] = {"added": added, "skipped": skipped}

    db.commit()
    return {
        "source_class_id": source_id,
        "disciplines_count": len(disc_ids),
        "results": summary,
    }


# ------------ TeacherClassSubject ------------

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
