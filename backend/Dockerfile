FROM python:3.12-slim

WORKDIR /app

# Dependências de sistema para psycopg2, reportlab, pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ build-essential \
    libpq-dev \
    libjpeg-dev zlib1g-dev libfreetype6-dev \
    netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

# Evita auto-upgrade do pip e torna downloads mais estáveis
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=120

# Copie primeiro requirements para aproveitar cache entre builds
COPY requirements.txt /app/requirements.txt

# Instala dependências Python (sem auto-upgrade do pip)
# Aumente timeout, sem cache, e com múltiplas tentativas
RUN python -m pip install --no-cache-dir --default-timeout=120 -r requirements.txt

# Copia o restante do código
COPY . /app

# Scripts (entrada e wait-for)
RUN chmod +x /app/scripts/*.sh

EXPOSE 8000

ENTRYPOINT ["/app/scripts/entrypoint.sh"]