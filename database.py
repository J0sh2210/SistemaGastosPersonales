import pyodbc
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus

# Cargar variables
load_dotenv()

# 1. Recuperar datos del .env
server = os.getenv("DB_SERVER")
database = os.getenv("DB_NAME")
username = os.getenv("DB_USER")
password = os.getenv("DB_PASS")

# 2. STRING PARA PYODBC (Este es el que soluciona tu error de "Driver")
# Al pasarlo así, el @ de tu contraseña NO causará problemas
DB_CONNECTION_STRING = (
    f"Driver={{ODBC Driver 17 for SQL Server}};"
    f"Server={server};"
    f"Database={database};"
    f"UID={username};"
    f"PWD={password};"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
    "Connection Timeout=30;"
)

# 3. STRING PARA SQLALCHEMY (Solo si lo usas para modelos ORM)
safe_password = quote_plus(password)
SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={quote_plus(DB_CONNECTION_STRING)}"

# Configuración de SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 4. TU FUNCIÓN ACTUALIZADA
# ... (Tus puntos 1, 2 y 3 se mantienen igual, están perfectos)

# 4. TU FUNCIÓN DEFINITIVA Y ROBUSTA
def ejecutar_sp(nombre_sp: str, params: list = None):
    results = []  # Inicializamos siempre como lista vacía para evitar errores de referencia
    try:
        # Usamos DB_CONNECTION_STRING directamente con pyodbc
        with pyodbc.connect(DB_CONNECTION_STRING, autocommit=True) as conn:
            with conn.cursor() as cursor:
                # Construcción del comando EXEC nombre_sp ?, ?, ?
                # Importante: SQL Server es estricto con las comas entre los ?
                placeholder = ', '.join(['?'] * len(params)) if params else ""
                sql = f"EXEC {nombre_sp} {placeholder}"
                
                # Ejecución
                cursor.execute(sql, params or [])
                
                # Bucle para capturar el conjunto de resultados correcto 
                # (A veces el primer set es solo el conteo de filas afectadas)
                while True:
                    if cursor.description:
                        columns = [column[0] for column in cursor.description]
                        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                        return results # Si encontramos datos, los devolvemos de inmediato
                    
                    if not cursor.nextset():
                        break
                
                # Si llegamos aquí y no hubo SELECT, pero el SP corrió bien:
                return [{"status": "success"}]

    except Exception as e:
        # Extraemos el mensaje de error de SQL si existe
        error_msg = str(e.args[1]) if len(e.args) > 1 else str(e)
        print(f"Error en DB ejecutando {nombre_sp}: {error_msg}")
        # Re-lanzamos el error para que el controlador (router) lo atrape
        raise Exception(error_msg)