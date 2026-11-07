import sys

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from app.db.session import get_engine


def main() -> int:
    try:
        engine = get_engine()
        try:
            with engine.connect() as connection:
                result = connection.scalar(text("SELECT 1"))
                if result != 1:
                    print("La consulta de prueba devolvió un resultado inesperado.")
                    return 1
        finally:
            engine.dispose()
    except ValidationError:
        print("Revisa las variables de SQL Server en el archivo .env.", file=sys.stderr)
        return 1
    except SQLAlchemyError as exc:
        print(
            f"No se pudo conectar a SQL Server ({type(exc).__name__}). "
            "Revisa el servidor, las credenciales, el certificado y el controlador ODBC.",
            file=sys.stderr,
        )
        return 1

    print("Conexión a SQL Server correcta (SELECT 1).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
