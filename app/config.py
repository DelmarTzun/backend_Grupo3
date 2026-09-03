from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la API y de Oracle desde variables de entorno / .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Grupo 3 - Análisis de Compras"
    app_env: str = "development"
    cors_origins: str = (
        "http://localhost:5173,"
        "http://localhost:3000,"
        "http://127.0.0.1:5500,"
        "http://localhost:5500"
    )

    oracle_user: str = ""
    oracle_password: str = ""
    oracle_host: str = "localhost"
    oracle_port: int = 1521
    oracle_service: str = "XEPDB1"
    oracle_dsn: str | None = None
    oracle_client_lib_dir: str | None = None

    pool_min: int = 1
    pool_max: int = 5
    pool_increment: int = 1

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def dsn(self) -> str:
        if self.oracle_dsn:
            return self.oracle_dsn
        return f"{self.oracle_host}:{self.oracle_port}/{self.oracle_service}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
