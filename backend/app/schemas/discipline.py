"""
=========================================================
SCHEMAS - DISCIPLINE
=========================================================
Validação de entrada e saída da API
"""

from pydantic import BaseModel, ConfigDict


class DisciplineCreate(BaseModel):
    name: str


class DisciplineOut(BaseModel):
    id: int
    name: str

    # Pydantic v2: revisar opção não migrada: from_attributes = True

    model_config = ConfigDict()
