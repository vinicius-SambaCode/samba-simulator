# backend/alembic/env.py
# -*- coding: utf-8 -*-
"""
Configuração do ambiente Alembic (migrações).

Objetivos:
- Ler a URL do banco a partir do settings (.env), ignorando alembic.ini.
- Garantir que o autogenerate enxerga TODAS as tabelas (importando os modelos).
- Definir target_metadata UMA única vez (Base.metadata).
- Ativar compare_type=True (detectar mudanças de tipo).
"""

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# ------------------------------------------------------------------------------
# 1) Colocar o diretório "backend/" no PYTHONPATH
#    Assim, conseguimos importar "app.*" quando o Alembic executar este arquivo.
# ------------------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ------------------------------------------------------------------------------
# 2) Importar settings, Base e TODOS os modelos do projeto
#    IMPORTANTE: estes imports DEVEM ocorrer ANTES de definir o target_metadata,
#    para que o autogenerate conheça todas as tabelas.
# ------------------------------------------------------------------------------
from app.core.settings import settings              # URL do banco (.env)
from app.models.base_models import Base             # Declarative Base (fonte única de metadata)

# Importa os módulos que REGISTRAM as tabelas no metadata:
# (A ordem aqui não é crítica entre eles, mas precisam vir ANTES do target_metadata)
from app.models import models                       # ex.: Discipline, e demais tabelas "clássicas"
from app.models import school                       # SchoolGrade, ClassSection, SchoolClass, Student
from app.models import exam                         # Exam, ExamDisciplineQuota, ExamTeacherAssignment, TeacherClassSubject, Question, ...
from app.models import refresh_token                # RefreshToken

# ------------------------------------------------------------------------------
# 3) Configuração básica do Alembic
# ------------------------------------------------------------------------------
config = context.config

# Carrega configuração de logging do alembic.ini (se existir)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Defina o metadata usado pelo autogenerate (APENAS UMA VEZ, depois dos imports)
target_metadata = Base.metadata

# ------------------------------------------------------------------------------
# 4) Execução em modo OFFLINE (gera SQL sem abrir conexão)
# ------------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """
    Executa migrações em modo 'offline'.
    Usa a URL do banco do settings (.env).
    """
    url = settings.DATABASE_URL  # Fonte de verdade: .env do backend

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,            # Detecta mudança de tipos (ex.: String -> Text)
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# ------------------------------------------------------------------------------
# 5) Execução em modo ONLINE (conecta e aplica/gera migrações)
# ------------------------------------------------------------------------------
def run_migrations_online() -> None:
    """
    Executa migrações em modo 'online'.
    Substitui sqlalchemy.url pela URL do settings (.env).
    """
    configuration = config.get_section(config.config_ini_section) or {}
    # Força a URL do banco a vir do settings (.env), ignorando alembic.ini
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Simples e suficiente para migrações
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,    # Detecta mudança de tipos
        )
        with context.begin_transaction():
            context.run_migrations()

# ------------------------------------------------------------------------------
# 6) Despacho: decide se roda offline ou online
# ------------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()