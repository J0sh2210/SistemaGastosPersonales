from sqlalchemy import Column, Integer, String
from database import Base

class Usuario(Base):
    __tablename__ = "Usuario"

    IdUsuario = Column(Integer, primary_key=True, index=True)
    PrimerNombre = Column(String)
    SegundoNombre = Column(String)
    PrimerApellido = Column(String)
    SegundoApellido = Column(String)
    RolUsuario = Column(String(1))