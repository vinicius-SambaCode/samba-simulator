# -*- coding: utf-8 -*-
"""
Shim de compatibilidade
-----------------------
Elimina duplicações antigas de segurança.
Reexporta o get_current_user e require_role canônicos.
"""

from app.core.security import get_current_user  # noqa: F401
from app.core.dependencies import require_role  # noqa: F401

__all__ = ["get_current_user", "require_role"]