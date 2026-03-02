# -*- coding: utf-8 -*-
"""
Schemas de autenticação e usuário (com Refresh Token)
"""

from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict


# ===============================
# LOGIN
# ===============================

class LoginIn(BaseModel):
    """ Útil se você quiser um login JSON em paralelo ao form-data. """
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    """
    Retorno padrão de tokens:
    - access_token: JWT curto
    - refresh_token: incluído para facilitar testes no Swagger
      (em produção, basta ler via cookie HttpOnly)
    """
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None


# ===============================
# REFRESH / LOGOUT
# ===============================

class RefreshIn(BaseModel):
    """
    Para o Swagger: permite enviar refresh no body.
    Se ausente, a rota lê do cookie HttpOnly automaticamente.
    """
    refresh_token: Optional[str] = None


class LogoutIn(BaseModel):
    """ logout_all=True => revoga todos os refresh do usuário (logout global). """
    logout_all: bool = False


# ===============================
# USER
# ===============================

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str  # validada contra tabela roles


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    roles: List[str]

    # Pydantic v2: revisar opção não migrada: from_attributes = True  # compatível com objetos ORM

    model_config = ConfigDict()
