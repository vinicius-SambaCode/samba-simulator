# app/schemas/student.py
# -*- coding: utf-8 -*-
"""
Schemas de Alunos — com validação de RA.

Regra do RA (São Paulo):
  O operador digita exatamente os 10 dígitos numéricos do RA.
  O sistema normaliza automaticamente para o formato de armazenamento:
    0000 + <10 dígitos>   →  14 caracteres no banco
    Ex.: digitado "1234567890"  →  armazenado "00001234567890"

  O décimo dígito digitado é o dígito verificador do RA.
  A normalização NÃO revalida o dígito — apenas garante formato.

  Qualquer RA existente no banco já está nesse formato normalizado,
  portanto buscas e comparações continuam funcionando corretamente.
"""

import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


def _normalize_ra(raw: str) -> str:
    """
    Remove qualquer separador (traço, ponto, barra, espaço) e
    valida que o resultado tem exatamente 10 dígitos numéricos.
    Retorna o RA no formato de 14 caracteres: '0000' + 10 dígitos.
    """
    digits = re.sub(r"[\s\.\-\/]", "", raw.strip())
    if not digits.isdigit():
        raise ValueError("O RA deve conter apenas dígitos numéricos.")
    if len(digits) != 10:
        raise ValueError(
            f"O RA deve ter exatamente 10 dígitos (recebido: {len(digits)}). "
            "Não inclua o prefixo 0000 — ele é adicionado automaticamente."
        )
    return "0000" + digits


class StudentCreate(BaseModel):
    ra:       str = Field(..., description="10 dígitos do RA (sem prefixo 0000)")
    name:     str = Field(..., description="Nome completo do aluno")
    class_id: int = Field(..., description="ID da turma (school_classes.id)")

    @field_validator("ra", mode="before")
    @classmethod
    def validate_ra(cls, v: str) -> str:
        return _normalize_ra(v)

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Nome muito curto.")
        return v


class StudentUpdate(BaseModel):
    ra:       Optional[str] = Field(None, description="10 dígitos do RA")
    name:     Optional[str] = Field(None, description="Nome completo do aluno")
    class_id: Optional[int] = Field(None, description="ID da turma")

    @field_validator("ra", mode="before")
    @classmethod
    def validate_ra(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _normalize_ra(v)


class StudentOut(BaseModel):
    id:       int
    ra:       str
    name:     str
    class_id: int

    model_config = ConfigDict(from_attributes=True)
