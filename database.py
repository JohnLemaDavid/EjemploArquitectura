from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import URL, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from config import get_settings


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    url = URL.create(
        "mssql+pyodbc",
        username=settings.sql_server_user,
        password=settings.sql_server_password.get_secret_value(),
        host=settings.sql_server_host,
        port=settings.sql_server_port,
        database=settings.sql_server_database,
        query={
            "driver": "ODBC Driver 18 for SQL Server",
            "Encrypt": "yes" if settings.sql_server_encrypt else "no",
            "TrustServerCertificate": (
                "yes" if settings.sql_server_trust_server_certificate else "no"
            ),
        },
    )
    return create_engine(
        url, pool_pre_ping=True, hide_parameters=True, connect_args={"timeout": 10}
    )


def get_session() -> Iterator[Session]:
    with Session(get_engine()) as session:
        yield session
