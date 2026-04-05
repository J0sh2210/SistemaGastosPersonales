import pyodbc
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus


load_dotenv()


server = os.getenv("DB_SERVER")
database = os.getenv("DB_NAME")
username = os.getenv("DB_USER")
password = os.getenv("DB_PASS")

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

safe_password = quote_plus(password)
SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={quote_plus(DB_CONNECTION_STRING)}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def ejecutar_sp(nombre_sp: str, params: list = None):
    results = [] 
    try:

        with pyodbc.connect(DB_CONNECTION_STRING, autocommit=True) as conn:
            with conn.cursor() as cursor:
                placeholder = ', '.join(['?'] * len(params)) if params else ""
                sql = f"EXEC {nombre_sp} {placeholder}"
                cursor.execute(sql, params or [])
                while True:
                    if cursor.description:
                        columns = [column[0] for column in cursor.description]
                        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                        return results 
                    
                    if not cursor.nextset():
                        break
                return [{"status": "success"}]

    except Exception as e:
        error_msg = str(e.args[1]) if len(e.args) > 1 else str(e)
        print(f"Error en DB ejecutando {nombre_sp}: {error_msg}")
        raise Exception(error_msg)