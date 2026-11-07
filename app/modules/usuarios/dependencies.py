from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.modules.usuarios.repositories.sql_usuario_repository import SqlUsuarioRepository
from app.modules.usuarios.service import UsuarioService


def get_usuario_service(session: Annotated[Session, Depends(get_session)]) -> UsuarioService:
    return UsuarioService(SqlUsuarioRepository(session))
