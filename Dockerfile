FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias base necesarias para Chrome
RUN apt-get update && apt-get install -y \
    wget curl unzip ca-certificates gnupg libnss3 libgbm1 libasound2 \
    libxshmfence1 libatk-bridge2.0-0 libdrm-dev libxkbcommon0 fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Instalar Chrome estable (última versión for-testing)
RUN CHROME_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE) && \
    wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chrome-linux64.zip" -O /tmp/chrome.zip && \
    unzip /tmp/chrome.zip -d /opt/ && \
    ln -sf /opt/chrome-linux64/chrome /usr/bin/google-chrome && \
    rm /tmp/chrome.zip

# Instalar ChromeDriver correspondiente
RUN CHROME_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE) && \
    wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip" -O /tmp/driver.zip && \
    unzip /tmp/driver.zip -d /usr/local/bin/ && \
    mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm /tmp/driver.zip

# Variables de entorno para Selenium
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

WORKDIR /app

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

EXPOSE 5000

CMD exec gunicorn --bind 0.0.0.0:${PORT:-5000} app:app
