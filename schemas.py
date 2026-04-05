from pydantic import BaseModel, EmailStr
from typing import Optional

class UsuarioRegistro(BaseModel):
    primer_nombre: str
    segundo_nombre: Optional[str] = None
    primer_apellido: str
    segundo_apellido: Optional[str] = None
    correo: EmailStr # Valida automáticamente que sea un email real
    telefono_wa: str
    provider_user_id: str
    contrasena: Optional[str] = None
    id_provider: int

class MensajeWhatsApp(BaseModel):
    telefono: str
    mensaje: str

class ConsultaMovimientoTotal(BaseModel):
    fecha_inicio: str
    fecha_fin: str
    categoria: Optional[str] = None

class consultaMovimientoCategoria(BaseModel):
    IdUsuario: int
    categoria: str
