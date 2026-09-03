from __future__ import annotations

from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Generator, Sequence

import oracledb
from fastapi import HTTPException

from app.config import Settings, get_settings

_pool: oracledb.ConnectionPool | None = None


def _serialize_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def rows_to_dicts(cursor: oracledb.Cursor) -> list[dict[str, Any]]:
    if cursor.description is None:
        return []
    columns = [col[0].lower() for col in cursor.description]
    return [
        {col: _serialize_value(val) for col, val in zip(columns, row)}
        for row in cursor.fetchall()
    ]


def init_oracle_client_if_needed(settings: Settings) -> None:
    """Thick mode solo si ORACLE_CLIENT_LIB_DIR está definido. Por defecto: Thin."""
    lib_dir = (settings.oracle_client_lib_dir or "").strip()
    if lib_dir:
        oracledb.init_oracle_client(lib_dir=lib_dir)


def create_pool(settings: Settings | None = None) -> oracledb.ConnectionPool:
    global _pool
    settings = settings or get_settings()

    if not settings.oracle_user or not settings.oracle_password:
        raise RuntimeError(
            "Faltan credenciales Oracle. Define ORACLE_USER y ORACLE_PASSWORD en .env"
        )

    init_oracle_client_if_needed(settings)
    _pool = oracledb.create_pool(
        user=settings.oracle_user,
        password=settings.oracle_password,
        dsn=settings.dsn,
        min=settings.pool_min,
        max=settings.pool_max,
        increment=settings.pool_increment,
    )
    return _pool


def get_pool() -> oracledb.ConnectionPool:
    if _pool is None:
        raise RuntimeError("El pool de Oracle no está inicializado")
    return _pool


def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


@contextmanager
def get_connection() -> Generator[oracledb.Connection, None, None]:
    pool = get_pool()
    connection = pool.acquire()
    try:
        yield connection
    finally:
        pool.release(connection)


def fetch_all(
    sql: str,
    params: Sequence[Any] | dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Ejecuta un SELECT y devuelve todas las filas como diccionarios."""
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, params or {})
                return rows_to_dicts(cursor)
    except oracledb.Error as exc:
        raise HTTPException(status_code=500, detail=f"Error Oracle: {exc}") from exc


def fetch_one(
    sql: str,
    params: Sequence[Any] | dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Ejecuta un SELECT y devuelve la primera fila o None."""
    rows = fetch_all(sql, params)
    return rows[0] if rows else None


def ping_database() -> dict[str, Any]:
    row = fetch_one("SELECT 1 AS ok, SYSDATE AS server_time FROM dual")
    settings = get_settings()
    return {
        "ok": True,
        "dsn": settings.dsn,
        "user": settings.oracle_user,
        "server_time": row["server_time"] if row else None,
        "driver_mode": "thick" if not oracledb.is_thin_mode() else "thin",
    }


def list_user_tables() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT table_name
        FROM user_tables
        ORDER BY table_name
        """
    )


def describe_table(table_name: str) -> list[dict[str, Any]]:
    safe_name = table_name.strip().upper()
    if not safe_name.replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="Nombre de tabla inválido")

    return fetch_all(
        """
        SELECT
            column_name,
            data_type,
            data_length,
            nullable,
            data_default
        FROM user_tab_columns
        WHERE table_name = :table_name
        ORDER BY column_id
        """,
        {"table_name": safe_name},
    )
