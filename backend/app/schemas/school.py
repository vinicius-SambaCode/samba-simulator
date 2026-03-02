# -*- coding: utf-8 -*-
"""
Schemas (Pydantic) para séries/anos, turmas (seções) e classes.
"""

from pydantic import BaseModel, ConfigDict
from enum import Enum


class EducationLevel(str, Enum):
    FUNDAMENTAL = "fundamental"
    MEDIO = "medio"


# ------------ Grades ------------
class GradeCreate(BaseModel):
    level: EducationLevel
    year_number: int
    label: str  # ex: "6º", "3ª"


class GradeOut(BaseModel):
    id: int
    level: EducationLevel
    year_number: int
    label: str

    # Pydantic v2: revisar opção não migrada: from_attributes = True

    model_config = ConfigDict()
# ------------ Sections ------------
class SectionCreate(BaseModel):
    label: str  # "A", "B", ...


class SectionOut(BaseModel):
    id: int
    label: str

    # Pydantic v2: revisar opção não migrada: from_attributes = True

    model_config = ConfigDict()
# ------------ Classes ------------
class ClassCreate(BaseModel):
    grade_id: int
    section_id: int


class ClassOut(BaseModel):
    id: int
    grade_id: int
    section_id: int
    name: str

    # Pydantic v2: revisar opção não migrada: from_attributes = True

    model_config = ConfigDict()
