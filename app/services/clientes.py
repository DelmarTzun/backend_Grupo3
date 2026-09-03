"""
EJEMPLO GUÍA — módulo de clientes.

IMPORTANTE PARA EL EQUIPO:
- El texto dentro de cada variable SQL = ... \"\"\" ... \"\"\" es Oracle puro.
- Se puede copiar TAL CUAL a SQL Developer (sin las comillas triples).
- No usen {variables} de Python dentro del SQL; eso no corre en SQL Developer.

Patrón:
1. Escribir la consulta SQL completa.
2. Probarla en SQL Developer.
3. Pegarla aquí y ejecutarla con fetch_all.
4. Exponerla en app/routers/clientes.py.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.database import fetch_all


def _respuesta(
    *,
    question: str,
    data: Any,
    unit: str,
    interpretation: str,
) -> dict[str, Any]:
    """Formato común de respuesta para el dashboard / presentación."""
    return {
        "question": question,
        "interpretation": interpretation,
        "unit": unit,
        "source": "Oracle Database · esquema DBA_COMPRAS",
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }


def top_por_monto() -> dict[str, Any]:
    """Top 10 clientes por monto total comprado."""
    # Copiar desde SELECT hasta el final → funciona en SQL Developer
    sql = """
        SELECT *
        FROM (
            SELECT
                c.id_cliente,
                TRIM(
                    c.primer_nombre
                    || ' '
                    || NVL2(c.segundo_nombre, c.segundo_nombre || ' ', '')
                    || c.primer_apellido
                    || NVL2(c.segundo_apellido, ' ' || c.segundo_apellido, '')
                ) AS nombre_cliente,
                ROUND(SUM(e.total_compra), 2) AS monto_total,
                COUNT(e.id_compra) AS num_compras
            FROM tbl_clientes c
            JOIN tbl_enc_compras e ON e.id_cliente = c.id_cliente
            GROUP BY
                c.id_cliente,
                c.primer_nombre, c.segundo_nombre,
                c.primer_apellido, c.segundo_apellido
            ORDER BY monto_total DESC
        )
        WHERE ROWNUM <= 10
    """
    data = fetch_all(sql)

    if data:
        top = data[0]
        interpretation = (
            f"El cliente con mayor consumo es {top['nombre_cliente']} "
            f"con Q{top['monto_total']:,.2f} en {int(top['num_compras'])} compras."
        )
    else:
        interpretation = "No hay compras registradas."

    return _respuesta(
        question="¿Quiénes son los 10 clientes con mayor monto total comprado?",
        data=data,
        unit="monto (Q)",
        interpretation=interpretation,
    )


def sin_compras() -> dict[str, Any]:
    """Clientes registrados que nunca han comprado."""
    sql = """
        SELECT
            c.id_cliente,
            TRIM(
                c.primer_nombre
                || ' '
                || NVL2(c.segundo_nombre, c.segundo_nombre || ' ', '')
                || c.primer_apellido
                || NVL2(c.segundo_apellido, ' ' || c.segundo_apellido, '')
            ) AS nombre_cliente,
            c.correo,
            c.telefono
        FROM tbl_clientes c
        WHERE NOT EXISTS (
            SELECT 1
            FROM tbl_enc_compras e
            WHERE e.id_cliente = c.id_cliente
        )
        ORDER BY c.id_cliente
    """
    data = fetch_all(sql)

    return _respuesta(
        question="¿Qué clientes no han realizado ninguna compra?",
        data=data,
        unit="clientes",
        interpretation=(
            f"Hay {len(data)} cliente(s) sin compras; candidatos a activación."
            if data
            else "Todos los clientes tienen al menos una compra."
        ),
    )


def ranking_por_monto() -> dict[str, Any]:
    """Posición de cada cliente con DENSE_RANK (función analítica)."""
    sql = """
        SELECT
            DENSE_RANK() OVER (ORDER BY SUM(e.total_compra) DESC) AS ranking,
            c.id_cliente,
            TRIM(
                c.primer_nombre
                || ' '
                || NVL2(c.segundo_nombre, c.segundo_nombre || ' ', '')
                || c.primer_apellido
                || NVL2(c.segundo_apellido, ' ' || c.segundo_apellido, '')
            ) AS nombre_cliente,
            ROUND(SUM(e.total_compra), 2) AS monto_total,
            COUNT(e.id_compra) AS num_compras
        FROM tbl_clientes c
        JOIN tbl_enc_compras e ON e.id_cliente = c.id_cliente
        GROUP BY
            c.id_cliente,
            c.primer_nombre, c.segundo_nombre,
            c.primer_apellido, c.segundo_apellido
        ORDER BY ranking
    """
    data = fetch_all(sql)

    return _respuesta(
        question="¿Cuál es la posición de cada cliente por monto (DENSE_RANK)?",
        data=data,
        unit="ranking / monto (Q)",
        interpretation=(
            f"Se rankearon {len(data)} clientes con compras usando DENSE_RANK."
            if data
            else "No hay clientes con compras."
        ),
    )
