import unittest
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.main import app
from app.modules.usuarios.dependencies import get_usuario_service
from app.modules.usuarios.repositories.sql_usuario_repository import SqlUsuarioRepository
from app.modules.usuarios.schemas import UsuarioResponse
from app.modules.usuarios.service import UsuarioService


class UsuariosTest(unittest.TestCase):
    def test_repository_filters_active_users_and_maps_only_public_fields(self):
        session = Mock()
        session.execute.return_value.mappings.return_value = [
            {"usuario": "jperez", "nombre": "Juan Pérez"}
        ]
        result = SqlUsuarioRepository(session).listar_activos()
        query, parameters = session.execute.call_args.args
        self.assertIn("ACTIVO = :activo", str(query))
        self.assertEqual(parameters, {"activo": True})
        self.assertEqual(result[0].model_dump(), {"usuario": "jperez", "nombre": "Juan Pérez"})

    def test_service_delegates_to_repository(self):
        repository = Mock()
        repository.listar_activos.return_value = []
        self.assertEqual(UsuarioService(repository).listar_activos(), [])
        repository.listar_activos.assert_called_once_with()

    def test_endpoint_returns_users_from_service(self):
        service = Mock()
        service.listar_activos.return_value = [UsuarioResponse(usuario="jperez", nombre="Juan Pérez")]
        app.dependency_overrides[get_usuario_service] = lambda: service
        self.addCleanup(app.dependency_overrides.clear)
        response = TestClient(app).get("/usuarios/activos")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{"usuario": "jperez", "nombre": "Juan Pérez"}])


if __name__ == "__main__":
    unittest.main()
