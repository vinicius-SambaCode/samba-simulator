"""
=========================================================
SCHEMAS - DISCIPLINE
=========================================================
Validação de entrada e saída da API
"""

from pydantic import BaseModel


class DisciplineCreate(BaseModel):
    name: str


class DisciplineOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True