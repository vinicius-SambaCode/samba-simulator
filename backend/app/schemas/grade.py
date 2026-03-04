# backend/app/schemas/grade.py
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal

EducationLevel = Literal["fundamental", "medio"]

class SchoolGradeBase(BaseModel):
    level: EducationLevel = Field(..., description="Nível: fundamental|medio")
    year_number: int = Field(..., ge=1, description="Número do ano/série (ex: 9)")
    label: str = Field(..., min_length=1, max_length=16, description="Rótulo que aparece (ex: '9º')")

class SchoolGradeCreate(SchoolGradeBase):
    pass

class SchoolGradeUpdate(SchoolGradeBase):
    pass

class SchoolGradeOut(SchoolGradeBase):
    id: int

    class Config:
        from_attributes = True
