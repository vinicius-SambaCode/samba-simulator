# app/schemas/student.py
# -*- coding: utf-8 -*-
"""
Schemas (Pydantic) para Alunos (students)
- Create/Update: entrada
- Out: saída (response)
- Filtros simples via query params nas rotas (class_id, ra)
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class StudentCreate(BaseModel):
    ra: str = Field(..., description="RA do aluno (único)")
    name: str = Field(..., description="Nome completo do aluno")
    class_id: int = Field(..., description="ID da turma (school_classes.id)")


class StudentUpdate(BaseModel):
    ra: Optional[str] = Field(None, description="RA do aluno (único)")
    name: Optional[str] = Field(None, description="Nome completo do aluno")
    class_id: Optional[int] = Field(None, description="ID da turma (school_classes.id)")


class StudentOut(BaseModel):
    id: int
    ra: str
    name: str
    class_id: int

    # Pydantic v2: revisar opção não migrada: from_attributes = True

    model_config = ConfigDict(from_attributes=True)
