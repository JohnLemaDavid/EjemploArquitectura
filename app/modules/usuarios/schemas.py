from pydantic import BaseModel


class UsuarioResponse(BaseModel):
    usuario: str
    nombre: str
