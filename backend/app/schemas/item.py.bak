"""
=========================================================
SCHEMAS - ITEM
=========================================================
"""

from pydantic import BaseModel
from typing import Optional
from app.models.base_models import DifficultyEnum, ItemTypeEnum


class ItemCreate(BaseModel):
    discipline_id: int
    skill_id: Optional[int]
    serie: str
    difficulty: DifficultyEnum
    item_type: ItemTypeEnum
    stem: str
    options_json: Optional[str] = None
    numeric_answer: Optional[str] = None
    media_url: Optional[str] = None
    latex: bool = False


class ItemOut(BaseModel):
    id: int
    serie: str
    difficulty: DifficultyEnum
    item_type: ItemTypeEnum
    stem: str

    class Config:
        from_attributes = True