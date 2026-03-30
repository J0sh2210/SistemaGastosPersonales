from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from UsuarioRegistroController import router as Usuario_router
from WhatsappController import router as Whatsapp_router

from sqlalchemy import text

app = FastAPI(title = "API de Gastos Personales")


# 🔌 Conexión a la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.include_router(Usuario_router)  
app.include_router(Whatsapp_router)  # Asegúrate de importar tu router de WhatsAppController.py y agregarlo aquí
# 🏠 Ruta base
@app.get("/")
def inicio():
    return {"mensaje": "API funcionando con SQL Server 🚀"}
