# 1. Usar una imagen base de Python
FROM python:3.11-slim

# 2. Instalar dependencias del sistema y el Driver de Microsoft SQL Server
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get clean

# 3. Directorio de trabajo
WORKDIR /app

# 4. Copiar archivos y instalar librerías de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar el resto del código
COPY . .

# 6. Comando para arrancar (Render usa el puerto 10000 por defecto)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]