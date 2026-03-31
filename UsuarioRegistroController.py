from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
from database import ejecutar_sp
from schemas import UsuarioRegistro

router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"]
)

@router.post("/usuarios/registrar")
async def registrar_usuario_completo(datos: UsuarioRegistro):

    try:
        resultado = ejecutar_sp("sp_RegistrarUsuarioCompleto", [
            datos.primer_nombre,
            datos.segundo_nombre,
            datos.primer_apellido,
            datos.segundo_apellido,
            datos.correo,
            datos.telefono_wa,
            datos.provider_user_id,
            datos.contrasena,
            datos.id_provider
          
        ])
        return {"mensaje": "Usuario registrado exitosamente", "data": resultado}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))