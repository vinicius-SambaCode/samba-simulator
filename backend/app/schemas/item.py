"""
=========================================================
SCHEMAS - ITEM
=========================================================
"""

from pydantic import BaseModel, ConfigDict
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

    # Pydantic v2: revisar opção não migrada: from_attributes = True

    model_config = ConfigDict(from_attributes=True)
