from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from UsuarioRegistroController import router as Usuario_router
from WhatsappController import router as Whatsapp_router

from sqlalchemy import text

app = FastAPI(title = "API de Gastos Personales")



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.include_router(Usuario_router)  
app.include_router(Whatsapp_router)  

@app.get("/")
def inicio():
    return {"mensaje": "API funcionando con SQL Server 🚀"}
