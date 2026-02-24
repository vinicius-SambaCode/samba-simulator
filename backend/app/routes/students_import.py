# app/routes/students_import.py
# -*- coding: utf-8 -*-
"""
Importação de alunos via CSV (somente "Ativo")
- POST /school/students/import  (COORDINATOR)

Parâmetros (query):
  - class_id: ID da turma (school_classes.id)
  - class_name: nome da turma (ex.: "3ªD") — exclusivo com class_id
  - dry_run: simulação sem gravar (default: True)
  - combine_check_digit: concatena RA + dígito (inclui 'X') (default: True)

CSV esperado (separador ';'), com possíveis linhas de relatório no topo:
Nº de chamada;Nome do Aluno;RA;Dig. RA;Data de Nascimento;Email Microsoft;Email Google;Situação do Aluno

Regras:
- Apenas "Ativo" (case-insensitive) será importado.
- RA final: concatenação RA + Dig. RA (quando combine_check_digit=True).
- Upsert por RA: se existe → atualiza (name, class_id); senão → cria.
"""

import csv
import io
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user
from app.core.dependencies import require_role
from app.models.base_models import User
from app.models.school import Student, SchoolClass

router = APIRouter(prefix="/school/students", tags=["school"])


def _resolve_class(
    db: Session,
    class_id: Optional[int],
    class_name: Optional[str]
) -> SchoolClass:
    if class_id is None and (class_name is None or not class_name.strip()):
        raise HTTPException(status_code=400, detail="Informe class_id OU class_name.")

    if class_id is not None and class_name:
        raise HTTPException(status_code=400, detail="Use apenas um parâmetro: class_id OU class_name.")

    if class_id is not None:
        cls = db.get(SchoolClass, class_id)
        if not cls:
            raise HTTPException(status_code=400, detail="Turma (class_id) inválida.")
        return cls

    # class_name informado
    cls = db.query(SchoolClass).filter(SchoolClass.name == class_name.strip()).first()
    if not cls:
        raise HTTPException(status_code=400, detail=f"Turma (class_name='{class_name}') não encontrada.")
    return cls


def _read_csv_starting_at_header(raw_bytes: bytes) -> csv.DictReader:
    """Decodifica o arquivo (utf-8-sig -> latin-1 se necessário),
    ignora linhas de relatório e cria um DictReader a partir do cabeçalho.
    """
    try:
        txt = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        txt = raw_bytes.decode("latin-1")

    # encontra a linha de cabeçalho (tem 'Nome do Aluno' e 'Situação do Aluno')
    header_line = None
    for line in txt.splitlines():
        if "Nome do Aluno" in line and "Situação do Aluno" in line and "RA" in line:
            header_line = line
            break
    if not header_line:
        raise HTTPException(status_code=400, detail="Cabeçalho não encontrado no CSV.")

    start_index = txt.find(header_line)
    sliced = io.StringIO(txt[start_index:])
    reader = csv.DictReader(sliced, delimiter=";")

    expected = ["Nome do Aluno", "RA", "Dig. RA", "Situação do Aluno"]
    missing = [c for c in expected if c not in (reader.fieldnames or [])]
    if missing:
        raise HTTPException(status_code=400, detail=f"Coluna(s) ausente(s): {missing}")
    return reader


@router.post("/import", dependencies=[Depends(require_role("COORDINATOR"))])
def import_students_csv(
    class_id: Optional[int] = Query(None, description="ID da turma (opcional, exclusivo com class_name)"),
    class_name: Optional[str] = Query(None, description="Nome da turma, ex.: '3ªD' (opcional, exclusivo com class_id)"),
    dry_run: bool = Query(True, description="Simula sem gravar"),
    combine_check_digit: bool = Query(True, description="Concatena RA + dígito (inclui 'X')"),
    file: UploadFile = File(..., description="CSV original exportado da rede"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:

    cls = _resolve_class(db, class_id=class_id, class_name=class_name)

    raw = file.file.read()
    reader = _read_csv_starting_at_header(raw)

    created = 0
    updated = 0
    skipped_inactive = 0
    skipped_invalid = 0
    examples_inactive = []
    examples_invalid = []

    for row in reader:
        try:
            status = (row.get("Situação do Aluno") or "").strip().upper()
            if status != "ATIVO":
                skipped_inactive += 1
                if len(examples_inactive) < 3:
                    examples_inactive.append({"Nome do Aluno": row.get("Nome do Aluno"), "status": row.get("Situação do Aluno")})
                continue

            name = (row.get("Nome do Aluno") or "").strip()
            ra_base = (row.get("RA") or "").strip()
            ra_dig = (row.get("Dig. RA") or "").strip()

            if not name or not ra_base:
                skipped_invalid += 1
                if len(examples_invalid) < 3:
                    examples_invalid.append({"row": row})
                continue

            ra_final = f"{ra_base}{ra_dig}" if (combine_check_digit and ra_dig) else ra_base

            # upsert por RA
            st = db.query(Student).filter(Student.ra == ra_final).first()
            if st:
                changed = False
                if st.name != name:
                    st.name = name
                    changed = True
                if st.class_id != cls.id:
                    st.class_id = cls.id
                    changed = True
                if changed:
                    db.add(st)
                    if not dry_run:
                        db.flush()
                    updated += 1
            else:
                st = Student(ra=ra_final, name=name, class_id=cls.id)
                db.add(st)
                if not dry_run:
                    db.flush()
                created += 1

        except Exception:
            skipped_invalid += 1
            if len(examples_invalid) < 3:
                examples_invalid.append({"row": row})

    if dry_run:
        db.rollback()
    else:
        db.commit()

    return {
        "detail": "Importação processada.",
        "dry_run": dry_run,
        "class_id": cls.id,
        "class_name": cls.name,
        "created": created,
        "updated": updated,
        "skipped_inactive": skipped_inactive,
        "skipped_invalid": skipped_invalid,
        "examples_inactive": examples_inactive,
        "examples_invalid": examples_invalid,
    }