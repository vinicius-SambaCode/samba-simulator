# -*- coding: utf-8 -*-
"""
Camada de segurança — JWT + HTTP Bearer + Refresh
-------------------------------------------------
- Swagger usa HTTPBearer (campo único "Authorize": Authorization: Bearer <token>)
- Access Token: JWT curto (HS256 / SECRET_KEY)
- Refresh Token: opaco, salvo com hash, com rotação/revogação

Este arquivo também concentra:
- hash/verify de senha (bcrypt via passlib)
- criação/decodificação de access token
- funções de emissão/validação/rotação/revogação de refresh token
- get_current_user padrão (depende de HTTPBearer)

Obs.: usamos PyJWT (import jwt) — compatível com seu projeto atual.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple
import secrets
import hashlib
import uuid

import jwt  # PyJWT
from passlib.context import CryptContext

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.core.db import get_db
from app.models.base_models import User
from app.models.refresh_token import RefreshToken


# ==========================================================
# Config helpers (com defaults caso não exista no settings)
# ==========================================================

def _cfg(name: str, default):
    """Lê do settings; se não existir, aplica default (evita editar settings.py agora)."""
    return getattr(settings, name, default)

ACCESS_TOKEN_EXPIRE_MINUTES: int = _cfg("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
REFRESH_TOKEN_EXPIRE_DAYS: int = _cfg("REFRESH_TOKEN_EXPIRE_DAYS", 14)
REFRESH_TOKEN_COOKIE_NAME: str = _cfg("REFRESH_TOKEN_COOKIE_NAME", "refresh_token")
REFRESH_TOKEN_COOKIE_SECURE: bool = _cfg("REFRESH_TOKEN_COOKIE_SECURE", False)  # True em produção (HTTPS)
REFRESH_TOKEN_COOKIE_SAMESITE: str = _cfg("REFRESH_TOKEN_COOKIE_SAMESITE", "lax")
REFRESH_TOKEN_PEPPER: str = _cfg("REFRESH_TOKEN_PEPPER", "CHANGE_ME_USE_ENV")


# ==========================================================
# Hash de senha (bcrypt)
# ==========================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Gera o hash seguro da senha usando bcrypt."""
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verifica se a senha informada corresponde ao hash armazenado."""
    return pwd_context.verify(password, password_hash)


# ==========================================================
# Access Token (JWT)
# ==========================================================

def create_access_token(subject: Dict[str, Any], expires_minutes: Optional[int] = None) -> str:
    """
    Cria um JWT com expiração.
    - subject deve conter ao menos {"sub": <user_id_str>}
    - você pode incluir outras claims (ex.: "roles": [...]) para conveniência
    """
    if expires_minutes is None:
        expires_minutes = ACCESS_TOKEN_EXPIRE_MINUTES

    now = datetime.now(tz=timezone.utc)
    expire_at = now + timedelta(minutes=expires_minutes)

    to_encode = {
        **subject,
        "exp": expire_at,  # expiração
        "iat": now,        # emitido em
        "nbf": now,        # não válido antes de
    }

    token = jwt.encode(
        payload=to_encode,
        key=settings.SECRET_KEY,
        algorithm="HS256",
    )
    return token


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodifica/valida o JWT.
    Retorna payload se válido; caso contrário, None.
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


# ==========================================================
# HTTP Bearer — esquema para Swagger (campo único "Authorize")
# ==========================================================

security = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Recupera o usuário autenticado a partir do Access Token (Bearer).
    1. Lê Authorization: Bearer <access_token>
    2. Decodifica JWT e obtém 'sub'
    3. Carrega o usuário no banco
    """
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_token(token)

    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: 'sub' incorreto.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get(User, user_id)
    if user is None or getattr(user, "is_active", True) is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# ==========================================================
# Refresh Token — helpers (hash/geração/expiração)
# ==========================================================

def _hash_refresh_token(token_plain: str) -> str:
    """
    Hash determinístico (SHA-256 + pepper) do refresh token opaco.
    (bcrypt não é necessário aqui e encarece leitura; SHA-256 cumpre o papel)
    """
    data = (REFRESH_TOKEN_PEPPER + token_plain).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _new_refresh_token_string() -> str:
    """Gera uma string opaca, longa e imprevisível (URL-safe)."""
    return secrets.token_urlsafe(64)


def _expiry_dt(days: int) -> datetime:
    return datetime.now(tz=timezone.utc) + timedelta(days=days)


# ==========================================================
# Refresh Token — emissão / validação / rotação / revogação
# ==========================================================

def issue_refresh_token(
    db: Session,
    user: User,
    user_agent: Optional[str],
    ip_address: Optional[str],
) -> Tuple[str, RefreshToken]:
    """
    Emite um refresh token:
    - Gera valor opaco (em claro) e salva APENAS seu HASH no banco.
    - Retorna (valor_em_claro, registro_orm).
    """
    token_plain = _new_refresh_token_string()
    token_hash = _hash_refresh_token(token_plain)

    record = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        jti=str(uuid.uuid4()),
        user_agent=(user_agent or "")[:256],
        ip_address=(ip_address or "")[:64],
        created_at=datetime.now(tz=timezone.utc),
        expires_at=_expiry_dt(REFRESH_TOKEN_EXPIRE_DAYS),
        revoked=False,
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    return token_plain, record


def _find_refresh_record(db: Session, token_plain: str) -> Optional[RefreshToken]:
    """Localiza o registro via HASH do refresh token em claro."""
    token_hash = _hash_refresh_token(token_plain)
    return db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()


def validate_refresh_token(db: Session, token_plain: str) -> RefreshToken:
    """
    Valida um refresh token:
    - existe
    - não revogado
    - não expirado
    Retorna o registro; lança 401 caso inválido.
    """
    rec = _find_refresh_record(db, token_plain)
    if not rec or rec.revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido.")
    if rec.expires_at <= datetime.now(tz=timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expirado.")
    return rec


def rotate_refresh_token(
    db: Session,
    old_record: RefreshToken,
    user_agent: Optional[str],
    ip_address: Optional[str],
) -> Tuple[str, RefreshToken]:
    """
    Rotação segura:
    - Marca o refresh antigo como revogado
    - Emite um novo refresh para o mesmo usuário
    - Encadeia via replaced_by (auditoria)
    """
    # Revoga o antigo
    old_record.revoked = True
    old_record.revoked_at = datetime.now(tz=timezone.utc)

    # Emite o novo
    new_plain, new_record = issue_refresh_token(db, old_record.user, user_agent, ip_address)

    # Encadeia
    old_record.replaced_by = new_record.jti
    db.add(old_record)
    db.commit()

    return new_plain, new_record


def revoke_refresh_token(db: Session, token_plain: str) -> None:
    """Revoga o refresh token informado (se existir e não estiver revogado)."""
    rec = _find_refresh_record(db, token_plain)
    if rec and not rec.revoked:
        rec.revoked = True
        rec.revoked_at = datetime.now(tz=timezone.utc)
        db.add(rec)
        db.commit()


def revoke_all_user_tokens(db: Session, user: User) -> int:
    """
    Revoga TODOS os refresh tokens ativos do usuário (logout global).
    Retorna a quantidade revogada.
    """
    q = db.query(RefreshToken).filter(RefreshToken.user_id == user.id, RefreshToken.revoked == False)  # noqa: E712
    now = datetime.now(tz=timezone.utc)
    count = 0
    for rec in q.all():
        rec.revoked = True
        rec.revoked_at = now
        db.add(rec)
        count += 1
    db.commit()
    return count