"""
=========================================================
SCHEMAS - SKILL
=========================================================
"""

from pydantic import BaseModel, ConfigDict


class SkillCreate(BaseModel):
    code: str
    description: str


class SkillOut(BaseModel):
    id: int
    code: str
    description: str

    # Pydantic v2: revisar opção não migrada: from_attributes = True

    model_config = ConfigDict()
