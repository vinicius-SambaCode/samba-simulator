# -*- coding: utf-8 -*-
"""
Pydantic Schemas para o módulo de Simulados (Sprint 1)
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class AnswerSource(str, Enum):
    TEACHERS = "teachers"
    COORDINATOR_OMR = "coordinator_omr"


class ExamStatus(str, Enum):
    DRAFT = "draft"
    COLLECTING = "collecting"
    REVIEW = "review"
    LOCKED = "locked"
    GENERATED = "generated"
    PUBLISHED = "published"


# ----------------------------
# Criar/editar simulado
# ----------------------------
class ExamCreate(BaseModel):
    title: str
    area: Optional[str] = None
    options_count: Literal[4, 5] = Field(..., description="4 (A-D) ou 5 (A-E)")
    answer_source: AnswerSource


class ExamOut(BaseModel):
    id: int
    title: str
    area: Optional[str]
    options_count: int
    answer_source: AnswerSource
    status: ExamStatus

    # Pydantic v2: revisar opção não migrada: from_attributes = True

    model_config = ConfigDict()
# ----------------------------
# Alocações e cotas
# ----------------------------
class AssignClassesIn(BaseModel):
    class_ids: List[int]


class QuotaItem(BaseModel):
    discipline_id: int
    quota: int


class SetQuotasIn(BaseModel):
    items: List[QuotaItem]


class AssignTeacherItem(BaseModel):
    class_id: int
    discipline_id: int
    teacher_user_id: int


class AssignTeachersIn(BaseModel):
    items: List[AssignTeacherItem]


# ----------------------------
# Questões (entrada simplificada no Sprint 1)
# ----------------------------
class QuestionOptionIn(BaseModel):
    label: str  # 'A'...'E'
    text: str


class QuestionCreate(BaseModel):
    class_id: int
    discipline_id: int
    stem: str
    options: List[QuestionOptionIn]
    # Quando answer_source == TEACHERS, o sistema aceita opcionalmente a correta aqui
    correct_label: Optional[str] = None


class BulkPasteIn(BaseModel):
    """
    Recebe um texto colado com uma ou mais questões.
    Formato mínimo sugerido no Sprint 1 (exemplo):
    Q: Enunciado...
    A) ...
    B) ...
    C) ...
    D) ...
    E) ...
    *GABARITO: C
    ---
    Q: Enunciado 2...
    ...
    """
    class_id: int
    discipline_id: int
    content: str