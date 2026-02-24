# -*- coding: utf-8 -*-
"""
Modelo ORM: RefreshToken
------------------------
Armazena SOMENTE o HASH do refresh token (segurança).
Suporta rotação (replaced_by) e revogação (revoked / revoked_at).
Cria backref "refresh_tokens" no User automaticamente.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship

# Importa a Base e o modelo User já existentes no seu projeto
from app.models.base_models import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Armazenamos só o HASH do token (nunca o valor em claro)
    token_hash = Column(String(128), nullable=False, unique=True, index=True)

    # ID único do refresh (para auditoria/encadeamento na rotação)
    jti = Column(String(36), nullable=False, index=True)

    # Metadados (opcionais) para auditoria e segurança
    user_agent = Column(String(256), nullable=True)
    ip_address = Column(String(64), nullable=True)

    # Controle de validade e rotação
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(tz=timezone.utc), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    replaced_by = Column(String(36), nullable=True)  # jti do novo token após rotação

    # Cria relação com User sem precisar editar o modelo User
    user = relationship("User", backref="refresh_tokens", lazy="joined")

    __table_args__ = (
        Index("ix_refresh_token_user_active", "user_id", "revoked"),
    )
