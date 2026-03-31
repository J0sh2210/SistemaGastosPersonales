# 1. Cambiamos a una imagen base un poco más robusta (bullseye)
FROM python:3.11-bullseye

# 2. Instalar dependencias del sistema y el Driver de Microsoft
# Añadimos limpieza de caché para evitar errores de espacio
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    apt-transport-https \
    unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# 3. Directorio de trabajo
WORKDIR /app

# 4. Copiar e instalar librerías de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar el resto del código
COPY . .

# 6. Comando para arrancar (Puerto 10000 para Render)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]