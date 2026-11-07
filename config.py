from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    sql_server_host: str = Field(min_length=1)
    sql_server_port: int = Field(ge=1, le=65535)
    sql_server_database: str = Field(min_length=1)
    sql_server_user: str = Field(min_length=1)
    sql_server_password: SecretStr
    sql_server_encrypt: bool = True
    sql_server_trust_server_certificate: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
