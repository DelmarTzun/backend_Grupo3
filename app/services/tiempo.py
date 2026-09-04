"""
Servicio de análisis temporal — consultas SQL.

SQL Oracle puro (copiable a SQL Developer).
Tabla: TBL_ENC_COMPRAS
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.database import fetch_all


from app.utils.responses import build_dashboard_response as _respuesta


def _mensual() -> list[dict[str, Any]]:
    sql = """
        WITH VentasMensuales AS (
            SELECT
                TO_CHAR(fecha_compra, 'YYYY-MM') AS mes,
                COUNT(id_compra) AS total_compras,
                ROUND(SUM(total_compra), 2) AS ingresos
            FROM tbl_enc_compras
            GROUP BY TO_CHAR(fecha_compra, 'YYYY-MM')
        )
        SELECT
            mes,
            total_compras,
            ingresos,
            ROUND(AVG(ingresos) OVER (), 2) AS promedio_mensual,
            LAG(ingresos, 1) OVER (ORDER BY mes) AS ingresos_mes_anterior,
            ROUND(
                (ingresos - LAG(ingresos, 1) OVER (ORDER BY mes))
                / NULLIF(LAG(ingresos, 1) OVER (ORDER BY mes), 0) * 100,
                2
            ) AS variacion_pct,
            DENSE_RANK() OVER (ORDER BY ingresos DESC) AS ranking_facturacion
        FROM VentasMensuales
        ORDER BY mes ASC
    """
    return fetch_all(sql)


def compras_por_mes() -> dict[str, Any]:
    """Total de compras por mes."""
    data = _mensual()
    if data:
        top = max(data, key=lambda r: r["total_compras"])
        interpretation = (
            f"El mes con más compras es {top['mes']} "
            f"({int(top['total_compras'])} compras)."
        )
    else:
        interpretation = "No hay compras en el histórico."

    return _respuesta(
        question="¿Cuántas compras se realizan por mes?",
        data=data,
        unit="compras",
        interpretation=interpretation,
    )


def ingresos_por_mes() -> dict[str, Any]:
    """Ingresos por mes y mes de mayor facturación."""
    data = _mensual()
    mes_mayor = max(data, key=lambda r: r["ingresos"]) if data else None
    if mes_mayor:
        interpretation = (
            f"El mes de mayor facturación es {mes_mayor['mes']} "
            f"con Q{mes_mayor['ingresos']:,.2f}."
        )
    else:
        interpretation = "No hay ingresos en el histórico."

    return _respuesta(
        question="¿Cuáles son los ingresos por mes y cuál facturó más?",
        data=data,
        unit="monto (Q)",
        interpretation=interpretation,
        extra={"mes_mayor_facturacion": mes_mayor},
    )


def evolucion_mensual() -> dict[str, Any]:
    """Tendencia, promedio mensual, variación % y ranking."""
    data = _mensual()
    if data:
        promedio = data[0]["promedio_mensual"]
        top = max(data, key=lambda r: r["ingresos"])
        variaciones = [r for r in data if r.get("variacion_pct") is not None]
        if variaciones:
            mayor_alza = max(variaciones, key=lambda r: r["variacion_pct"])
            interpretation = (
                f"Promedio mensual Q{promedio:,.2f}. "
                f"Mayor facturación: {top['mes']} (Q{top['ingresos']:,.2f}). "
                f"Mayor alza: {mayor_alza['mes']} ({mayor_alza['variacion_pct']}%)."
            )
        else:
            interpretation = (
                f"Promedio mensual Q{promedio:,.2f}. "
                f"Mayor facturación: {top['mes']} (Q{top['ingresos']:,.2f})."
            )
    else:
        interpretation = "No hay compras en el histórico."

    return _respuesta(
        question="¿Cómo evolucionó la facturación mensual, el promedio y la variación %?",
        data=data,
        unit="monto (Q) / porcentaje (%)",
        interpretation=interpretation,
    )


def ranking_meses() -> dict[str, Any]:
    """Ranking de meses por facturación."""
    data = sorted(_mensual(), key=lambda r: r["ranking_facturacion"])
    if data:
        interpretation = (
            f"El mes #1 por facturación es {data[0]['mes']} "
            f"con Q{data[0]['ingresos']:,.2f}."
        )
    else:
        interpretation = "No hay meses para rankear."

    return _respuesta(
        question="¿Cómo se rankean los meses por facturación?",
        data=data,
        unit="ranking / monto (Q)",
        interpretation=interpretation,
    )
