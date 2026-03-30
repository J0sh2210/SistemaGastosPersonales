from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus 

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
print("RUTA .env:", os.path.join(os.path.dirname(__file__), ".env"))
print("EXISTE:", os.path.exists(os.path.join(os.path.dirname(__file__), ".env")))
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

print("USER:", os.getenv("DB_USER"))
print("PASS:", os.getenv("DB_PASS"))


password = quote_plus(DB_PASS)

DATABASE_URL = f"mssql+pyodbc://{DB_USER}:{password}@{DB_HOST}:1433/{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server&timeout=30&Encrypt=yes&TrustServerCertificate=yes&Connection+Timeout=30"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()