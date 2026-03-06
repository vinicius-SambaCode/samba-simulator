# -*- coding: utf-8 -*-
"""
Rotas de Autenticação (Access + Refresh)
----------------------------------------
- /auth/login   : emite access + refresh (cookie HttpOnly + corpo p/ Swagger)
- /auth/refresh : rotaciona refresh e retorna novos tokens
- /auth/logout  : revoga refresh atual (ou todos, se logout_all=True)
- /auth/me      : retorna usuário autenticado

Notas:
- Access Token curto (JWT HS256)
- Refresh Token opaco, armazenado com hash
- Swagger: botão "Authorize" continua com HTTPBearer (campo único)
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Banco
from app.core.db import get_db

# Segurança
from app.core.security import (
    verify_password,
    hash_password,
    create_access_token,
    get_current_user,
    issue_refresh_token,
    validate_refresh_token,
    rotate_refresh_token,
    revoke_refresh_token,
    revoke_all_user_tokens,
)

# RBAC
from app.core.deps import require_role

# Schemas
from app.schemas.auth import (
    TokenOut,
    UserCreate,
    UserOut,
    RefreshIn,
    LogoutIn,
)

# Models
from app.models.base_models import User, Role
from app.core.settings import settings


router = APIRouter(prefix="/auth", tags=["auth"])


# ----------------------------------------------------------
# Cookies utilitários (HttpOnly para refresh)
# ----------------------------------------------------------

def _set_refresh_cookie(resp: Response, refresh_token: str) -> None:
    """
    Seta o cookie HttpOnly do refresh.
    Em produção, ative SECURE=True e avalie SameSite conforme o front.
    """
    resp.set_cookie(
        key=getattr(settings, "REFRESH_TOKEN_COOKIE_NAME", "refresh_token"),
        value=refresh_token,
        httponly=True,
        secure=getattr(settings, "REFRESH_TOKEN_COOKIE_SECURE", False),
        samesite=getattr(settings, "REFRESH_TOKEN_COOKIE_SAMESITE", "lax"),
        max_age=getattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", 14) * 24 * 3600,
        path="/auth",  # restringe envio automático do cookie
    )


def _clear_refresh_cookie(resp: Response) -> None:
    resp.delete_cookie(
        key=getattr(settings, "REFRESH_TOKEN_COOKIE_NAME", "refresh_token"),
        path="/auth",
    )


def _extract_refresh_from_cookie_or_body(req: Request, body: Optional[RefreshIn]) -> Optional[str]:
    """
    Prioriza o body (Swagger-friendly).
    Se ausente, tenta o cookie HttpOnly.
    """
    if body and body.refresh_token:
        return body.refresh_token
    return req.cookies.get(getattr(settings, "REFRESH_TOKEN_COOKIE_NAME", "refresh_token"))


# ==========================================================
# LOGIN (form-data padrão do Swagger)
# ==========================================================

@router.post("/login", response_model=TokenOut)
def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login via form-data (username -> email, password).
    Retorna:
    - access_token (JWT) no body
    - refresh_token no body (para testes) e via cookie HttpOnly
    """
    # 1) Busca usuário por e-mail
    user = db.query(User).filter(User.email == form_data.username).first()

    # 2) Valida senha
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")

    # 3) Cria Access Token (curto)
    access_token = create_access_token({
        "sub": str(user.id),
        "roles": [r.name for r in user.roles],
    })

    # 4) Emite Refresh Token (persistido com hash) + captura metadados
    user_agent = request.headers.get("user-agent", "")
    ip = request.client.host if request.client else None
    refresh_token, _rec = issue_refresh_token(db, user, user_agent, ip)

    # 5) Seta cookie HttpOnly e retorna no body (para facilitar Swagger)
    _set_refresh_cookie(response, refresh_token)
    return TokenOut(access_token=access_token, refresh_token=refresh_token)


# ==========================================================
# REFRESH (rotação)
# ==========================================================

@router.post("/refresh", response_model=TokenOut)
def refresh_token(
    request: Request,
    response: Response,
    payload: RefreshIn | None = None,
    db: Session = Depends(get_db),
):
    """
    Troca um refresh válido por NOVOS tokens (access + refresh).
    - Aceita refresh no cookie OU no body (Swagger-friendly).
    - Aplica rotação: o refresh antigo é revogado.
    """
    provided = _extract_refresh_from_cookie_or_body(request, payload)
    if not provided:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token ausente.")

    # 1) Valida refresh atual
    rec = validate_refresh_token(db, provided)

    # 2) Rotaciona
    user_agent = request.headers.get("user-agent", "")
    ip = request.client.host if request.client else None
    new_refresh, _new_rec = rotate_refresh_token(db, rec, user_agent, ip)

    # 3) Novo Access Token
    user = rec.user  # carregado via relationship
    new_access = create_access_token({
        "sub": str(user.id),
        "roles": [r.name for r in user.roles],
    })

    # 4) Atualiza cookie e retorna no body
    _set_refresh_cookie(response, new_refresh)
    return TokenOut(access_token=new_access, refresh_token=new_refresh)


# ==========================================================
# LOGOUT
# ==========================================================

@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    body: LogoutIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Logout:
    - logout_all=True: revoga TODOS os refresh do usuário (logout global)
    - logout_all=False: revoga apenas o refresh atual (cookie/body/header)
    """
    if body.logout_all:
        count = revoke_all_user_tokens(db, current_user)
        _clear_refresh_cookie(response)
        return {"detail": f"Logout global concluído. Tokens revogados: {count}."}

    # Revoga apenas o atual
    provided = request.cookies.get(getattr(settings, "REFRESH_TOKEN_COOKIE_NAME", "refresh_token"))
    if not provided:
        # Opções extras para Swagger/integrações
        provided = request.headers.get("X-Refresh-Token")
    if not provided and isinstance(body, LogoutIn):
        # (Opcional) se você quiser aceitar via body também, adicione um campo aqui
        pass

    if not provided:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token ausente.")

    revoke_refresh_token(db, provided)
    _clear_refresh_cookie(response)
    return {"detail": "Logout concluído."}


# ==========================================================
# /me (usuário autenticado)
# ==========================================================

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return UserOut(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        roles=[r.name for r in current_user.roles],
    )


# ==========================================================
# Criar usuário (apenas ADMIN)
# ==========================================================

@router.post(
    "/users",
    response_model=UserOut,
    dependencies=[Depends(require_role("ADMIN"))]
)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
):
    exists = db.query(User).filter(User.email == data.email).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado")

    role = db.query(Role).filter(Role.name == data.role).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role inválida")

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        is_active=True
    )
    user.roles.append(role)

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        roles=[r.name for r in user.roles],
    )
