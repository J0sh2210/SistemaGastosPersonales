from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.models import Usuario
from sqlalchemy import text

app = FastAPI()


# 🔌 Conexión a la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🏠 Ruta base
@app.get("/")
def inicio():
    return {"mensaje": "API funcionando con SQL Server 🚀"}
