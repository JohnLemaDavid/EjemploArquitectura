from app.modules.usuarios.repositories.sql_usuario_repository import SqlUsuarioRepository
from app.modules.usuarios.schemas import UsuarioResponse


class UsuarioService:
    def __init__(self, repository: SqlUsuarioRepository) -> None:
        self.repository = repository

    def listar_activos(self) -> list[UsuarioResponse]:
        return self.repository.listar_activos()
