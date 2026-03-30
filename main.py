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

@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"ok": True}

# 🏠 Ruta base
@app.get("/")
def inicio():
    return {"mensaje": "API funcionando con SQL Server 🚀"}

# 📄 Obtener todos los usuarios
@app.get("/usuarios")
def obtener_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()

# 🔍 Obtener usuario por ID
@app.get("/usuarios/{id_usuario}")
def obtener_usuario(id_usuario: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.IdUsuario == id_usuario).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return usuario

# ➕ Crear usuario
@app.post("/usuarios")
def crear_usuario(
    PrimerNombre: str,
    SegundoNombre: str,
    PrimerApellido: str,
    SegundoApellido: str,
    RolUsuario: str,
    db: Session = Depends(get_db)
):
    # ⚠️ Validación del rol (CHAR(1))
    if len(RolUsuario) != 1:
        raise HTTPException(status_code=400, detail="El rol debe ser un solo carácter")

    nuevo = Usuario(
        PrimerNombre=PrimerNombre,
        SegundoNombre=SegundoNombre,
        PrimerApellido=PrimerApellido,
        SegundoApellido=SegundoApellido,
        RolUsuario=RolUsuario
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)  # 🔥 obtiene IDENTITY

    return nuevo

# ✏️ Actualizar usuario
@app.put("/usuarios/{id_usuario}")
def actualizar_usuario(
    id_usuario: int,
    PrimerNombre: str,
    SegundoNombre: str,
    PrimerApellido: str,
    SegundoApellido: str,
    RolUsuario: str,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.IdUsuario == id_usuario).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if len(RolUsuario) != 1:
        raise HTTPException(status_code=400, detail="El rol debe ser un solo carácter")

    usuario.PrimerNombre = PrimerNombre
    usuario.SegundoNombre = SegundoNombre
    usuario.PrimerApellido = PrimerApellido
    usuario.SegundoApellido = SegundoApellido
    usuario.RolUsuario = RolUsuario

    db.commit()
    return usuario

# ❌ Eliminar usuario
@app.delete("/usuarios/{id_usuario}")
def eliminar_usuario(id_usuario: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.IdUsuario == id_usuario).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.delete(usuario)
    db.commit()

    return {"mensaje": "Usuario eliminado correctamente"}