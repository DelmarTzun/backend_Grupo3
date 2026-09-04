"""
Servicio de tarjetas — consultas SQL.

SQL Oracle puro (copiable a SQL Developer).
Tablas: TBL_TARJETAS, TBL_MARCAS, TBL_ENC_COMPRAS, TBL_CLIENTES
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
    return {
        "question": question,
        "interpretation": interpretation,
        "unit": unit,
        "source": "Oracle Database · esquema DBA_COMPRAS",
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }


def marcas_resumen() -> dict[str, Any]:
    """Marcas: compras, monto, ticket promedio y participación %."""
    sql = """
        SELECT
            m.id_marca,
            m.nombre_marca,
            COUNT(e.id_compra) AS num_compras,
            ROUND(SUM(e.total_compra), 2) AS monto_total,
            ROUND(AVG(e.total_compra), 2) AS ticket_promedio,
            ROUND(
                RATIO_TO_REPORT(SUM(e.total_compra)) OVER () * 100,
                2
            ) AS participacion_pct
        FROM tbl_enc_compras e
        JOIN tbl_tarjetas t ON t.id_tarjeta = e.id_tarjeta
        JOIN tbl_marcas m ON m.id_marca = t.id_marca
        GROUP BY m.id_marca, m.nombre_marca
        ORDER BY monto_total DESC
    """
    data = fetch_all(sql)
    if data:
        top = data[0]
        interpretation = (
            f"{top['nombre_marca']} lidera con Q{top['monto_total']:,.2f} "
            f"({top['participacion_pct']}% del monto) y "
            f"{int(top['num_compras'])} compras."
        )
    else:
        interpretation = "No hay compras asociadas a tarjetas."

    return _respuesta(
        question="¿Cómo se distribuyen las ventas y compras por marca de tarjeta?",
        data=data,
        unit="monto (Q) / compras / porcentaje (%)",
        interpretation=interpretation,
    )


def credito_vs_debito() -> dict[str, Any]:
    """Comparación crédito vs débito."""
    sql = """
        SELECT
            UPPER(t.tipo_tarjeta) AS tipo_tarjeta,
            COUNT(e.id_compra) AS total_compras,
            ROUND(SUM(e.total_compra), 2) AS monto_total,
            ROUND(AVG(e.total_compra), 2) AS promedio_gasto
        FROM tbl_enc_compras e
        JOIN tbl_tarjetas t ON t.id_tarjeta = e.id_tarjeta
        GROUP BY UPPER(t.tipo_tarjeta)
        ORDER BY monto_total DESC
    """
    data = fetch_all(sql)
    if len(data) >= 2:
        a, b = data[0], data[1]
        interpretation = (
            f"{a['tipo_tarjeta']} supera a {b['tipo_tarjeta']} en monto "
            f"(Q{a['monto_total']:,.2f} vs Q{b['monto_total']:,.2f})."
        )
    elif data:
        interpretation = f"Solo hay movimientos de tipo {data[0]['tipo_tarjeta']}."
    else:
        interpretation = "No hay datos de tipo de tarjeta."

    return _respuesta(
        question="¿Cómo se comparan crédito y débito en compras y montos?",
        data=data,
        unit="monto (Q) / compras",
        interpretation=interpretation,
    )


def promedio_por_tipo() -> dict[str, Any]:
    """Promedio de gasto por tipo de tarjeta."""
    sql = """
        SELECT
            UPPER(t.tipo_tarjeta) AS tipo_tarjeta,
            ROUND(AVG(e.total_compra), 2) AS gasto_promedio,
            COUNT(e.id_compra) AS num_compras
        FROM tbl_enc_compras e
        JOIN tbl_tarjetas t ON t.id_tarjeta = e.id_tarjeta
        GROUP BY UPPER(t.tipo_tarjeta)
        ORDER BY gasto_promedio DESC
    """
    data = fetch_all(sql)
    if data:
        top = data[0]
        interpretation = (
            f"El ticket promedio más alto es de {top['tipo_tarjeta']}: "
            f"Q{top['gasto_promedio']:,.2f}."
        )
    else:
        interpretation = "No hay datos de gasto por tipo de tarjeta."

    return _respuesta(
        question="¿Cuál es el promedio de gasto por tipo de tarjeta?",
        data=data,
        unit="monto (Q)",
        interpretation=interpretation,
    )


def clientes_multiples_tarjetas() -> dict[str, Any]:
    """Clientes con más de una tarjeta."""
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
            COUNT(t.id_tarjeta) AS total_tarjetas
        FROM tbl_clientes c
        JOIN tbl_tarjetas t ON t.id_cliente = c.id_cliente
        GROUP BY
            c.id_cliente,
            c.primer_nombre, c.segundo_nombre,
            c.primer_apellido, c.segundo_apellido
        HAVING COUNT(t.id_tarjeta) > 1
        ORDER BY total_tarjetas DESC, c.id_cliente
    """
    data = fetch_all(sql)
    return _respuesta(
        question="¿Qué clientes poseen más de una tarjeta registrada?",
        data=data,
        unit="tarjetas",
        interpretation=(
            f"{len(data)} cliente(s) tienen más de una tarjeta."
            if data
            else "Ningún cliente tiene más de una tarjeta."
        ),
    )
