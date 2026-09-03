from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.database import describe_table, list_user_tables, ping_database
from app.schemas.common import HealthResponse

router = APIRouter(tags=["salud"])


@router.get("/health", response_model=HealthResponse)
def health(check_db: bool = False) -> HealthResponse:
    """Estado de la API. Con ?check_db=true también valida Oracle."""
    settings = get_settings()
    database = None

    if check_db:
        try:
            database = ping_database()
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"API activa, pero Oracle no responde: {exc}",
            ) from exc

    return HealthResponse(
        status="ok",
        app=settings.app_name,
        env=settings.app_env,
        database=database,
    )


@router.get("/meta/tables")
def get_tables() -> dict:
    """Lista tablas del esquema (ayuda para escribir SQL)."""
    tables = list_user_tables()
    return {
        "count": len(tables),
        "tables": [row["table_name"] for row in tables],
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/meta/tables/{table_name}")
def get_table_structure(table_name: str) -> dict:
    """Describe columnas de una tabla."""
    columns = describe_table(table_name)
    if not columns:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró la tabla '{table_name}' en el esquema actual",
        )
    return {
        "table": table_name.upper(),
        "columns": columns,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }
