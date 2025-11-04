FROM python:3.11-slim

# Evitar preguntas interactivas en la instalación
ENV DEBIAN_FRONTEND=noninteractive

# Instalar Chromium y dependencias mínimas
RUN apt-get update && apt-get install -y \
    chromium chromium-driver \
    libnss3 libgconf-2-4 libxi6 libgbm1 libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Establecer variables de entorno para Selenium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer puerto
EXPOSE 5000

# Ejecutar con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
