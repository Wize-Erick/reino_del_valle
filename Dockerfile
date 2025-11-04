FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias base para Playwright
RUN apt-get update && apt-get install -y curl wget unzip fonts-liberation libnss3 libatk-bridge2.0-0 libxkbcommon0 libgbm1 libasound2 && \
    pip install --no-cache-dir playwright flask gunicorn && \
    playwright install --with-deps chromium && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

EXPOSE 5000
CMD exec gunicorn --bind 0.0.0.0:${PORT:-5000} app:app
