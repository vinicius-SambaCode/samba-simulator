"""
Script temporário para criar todas as tabelas.
Use apenas em ambiente de desenvolvimento.
"""

from app.core.db import engine, Base

# IMPORTANTE:
# precisamos importar os models
# para que eles sejam registrados no metadata

print("Criando tabelas...")

Base.metadata.create_all(bind=engine)

print("Tabelas criadas com sucesso!")