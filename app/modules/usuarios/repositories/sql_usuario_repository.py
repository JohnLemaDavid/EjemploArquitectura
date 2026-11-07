from sqlalchemy import text
from sqlalchemy.orm import Session

from app.modules.usuarios.schemas import UsuarioResponse


class SqlUsuarioRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def listar_activos(self) -> list[UsuarioResponse]:
        result = self.session.execute(
            text(
                "SELECT USUARIO AS usuario, NOMBRE AS nombre "
                "FROM SEGURIDAD.USUARIO WHERE ACTIVO = :activo ORDER BY USUARIO"
            ),
            {"activo": 1},
        )
        return [UsuarioResponse.model_validate(row) for row in result.mappings()]
