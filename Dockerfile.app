# Dockerfile.app
FROM python:3.12-slim

# Empêche Python de générer des fichiers .pyc et assure un log en temps réel
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installation des dépendances système (Postgres+ Playwright)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    # Dépendances système pour Chromium (inclut libnspr4 et libnss3)
    libnss3 libnspr4 libasound2 libatk1.0-0 libc6 libcups2 libdbus-1-3 \
    libexpat1 libfontconfig1 libgbm1 libgcc1 libglib2.0-0 libgtk-3-0 \
    libpango-1.0-0 libx11-6 libxcomposite1 libxdamage1 libxext6 libxfixes3 \
    libxi6 libxrandr2 libxrender1 libxss1 libxtst6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copie et installation des dépendances
COPY requirements-app.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Installation de chromium
RUN python -m playwright install chromium
RUN python -m playwright install-deps chromium
