
# backend/app/core/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Metadados básicos
    APP_NAME: str = "SAMBA-Simulator"
    ENV: str = "dev"

    # Segurança / Auth
    SECRET_KEY: str = "change-this-in-.env"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Banco de dados (usaremos DATABASE_URL diretamente)
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "samba_simulator"

    # URL completa do banco (sobrepõe os campos acima se presente no .env)
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/samba_simulator"

    # CORS (frontend local)
    CORS_ORIGINS: str = "http://localhost:5500,http://127.0.0.1:5500"

    # Onde está o .env (executando a API a partir de backend/)
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # ignora variáveis inesperadas
    )

# >>> ESTE É O OBJETO QUE O ALEMBIC E A API IMPORTAM <<<
settings = Settings()
