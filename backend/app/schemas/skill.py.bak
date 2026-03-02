"""
=========================================================
SCHEMAS - SKILL
=========================================================
"""

from pydantic import BaseModel


class SkillCreate(BaseModel):
    code: str
    description: str


class SkillOut(BaseModel):
    id: int
    code: str
    description: str

    class Config:
        from_attributes = True