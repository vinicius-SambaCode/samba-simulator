FROM python:3.12-slim

WORKDIR /app

# Dependências do sistema para psycopg2, reportlab, pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ build-essential \
    libpq-dev \
    libjpeg-dev zlib1g-dev libfreetype6-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia tudo
COPY . /app

# Scripts (entrada e wait-for)
RUN chmod +x /app/scripts/*.sh

# Porta da API
EXPOSE 8000

ENTRYPOINT ["/app/scripts/entrypoint.sh"]