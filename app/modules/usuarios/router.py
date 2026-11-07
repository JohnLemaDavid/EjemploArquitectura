from typing import Annotated

from fastapi import APIRouter, Depends

from app.modules.usuarios.dependencies import get_usuario_service
from app.modules.usuarios.schemas import UsuarioResponse
from app.modules.usuarios.service import UsuarioService

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/activos", response_model=list[UsuarioResponse])
def listar_usuarios_activos(
    service: Annotated[UsuarioService, Depends(get_usuario_service)],
) -> list[UsuarioResponse]:
    return service.listar_activos()
