# Dockerfile.app
FROM python:3.12-slim

# Installation des dépendances système pour Postgres
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copie et installation des dépendances
COPY requirements-app.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# On ne copie pas le code ici, on utilisera les volumes du docker-compose