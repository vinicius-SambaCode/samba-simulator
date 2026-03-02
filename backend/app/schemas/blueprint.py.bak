"""
Schemas do Blueprint
Responsável pela validação de entrada e saída da API
"""

from pydantic import BaseModel
from typing import Optional


# ==============================
# ENTRADA (CREATE)
# ==============================

class BlueprintIn(BaseModel):
    name: str
    description: Optional[str] = None


# ==============================
# SAÍDA (RESPONSE)
# ==============================

class BlueprintOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True  # SQLAlchemy 2.0