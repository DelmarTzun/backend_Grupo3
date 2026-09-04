"""
Servicio de KPIs del dashboard — consultas SQL.

SQL Oracle puro (copiable a SQL Developer).
"""

from __future__ import annotations

from typing import Any

from app.database import fetch_one


from app.utils.responses import build_dashboard_response as _respuesta


def obtener_resumen_kpis() -> dict[str, Any]:
    """KPIs globales del dashboard."""
    resumen = fetch_one(
        """
        SELECT
            ROUND(NVL(SUM(total_compra), 0), 2) AS monto_total,
            COUNT(*) AS total_compras,
            ROUND(NVL(AVG(total_compra), 0), 2) AS ticket_promedio,
            COUNT(DISTINCT id_cliente) AS clientes_activos,
            MIN(fecha_compra) AS fecha_min,
            MAX(fecha_compra) AS fecha_max
        FROM tbl_enc_compras
        """
    ) or {}

    producto = fetch_one(
        """
        SELECT *
        FROM (
            SELECT
                p.id_producto,
                p.nombre_producto,
                SUM(d.cantidad) AS cantidad_total,
                ROUND(SUM(d.subtotal), 2) AS ingresos
            FROM tbl_det_compras d
            JOIN tbl_productos p ON p.id_producto = d.id_producto
            GROUP BY p.id_producto, p.nombre_producto
            ORDER BY cantidad_total DESC, ingresos DESC
        )
        WHERE ROWNUM = 1
        """
    )

    categoria = fetch_one(
        """
        SELECT *
        FROM (
            SELECT
                cat.id_categoria,
                cat.nombre_categoria,
                ROUND(SUM(d.subtotal), 2) AS monto_ventas
            FROM tbl_det_compras d
            JOIN tbl_productos p ON p.id_producto = d.id_producto
            JOIN tbl_categorias cat ON cat.id_categoria = p.id_categoria
            GROUP BY cat.id_categoria, cat.nombre_categoria
            ORDER BY monto_ventas DESC
        )
        WHERE ROWNUM = 1
        """
    )

    data = {
        "monto_total": resumen.get("monto_total", 0),
        "total_compras": resumen.get("total_compras", 0),
        "ticket_promedio": resumen.get("ticket_promedio", 0),
        "clientes_activos": resumen.get("clientes_activos", 0),
        "producto_mas_vendido": producto,
        "categoria_mayor_venta": categoria,
        "intervalo": {
            "fecha_min": resumen.get("fecha_min"),
            "fecha_max": resumen.get("fecha_max"),
        },
    }
    interpretation = (
        f"Facturación Q{data['monto_total']:,.2f} en "
        f"{int(data['total_compras'])} compras; "
        f"ticket promedio Q{data['ticket_promedio']:,.2f}; "
        f"{int(data['clientes_activos'])} clientes activos."
    )
    return _respuesta(
        question="¿Cuáles son los indicadores clave (KPIs) globales del negocio?",
        data=data,
        unit="monto (Q) / compras / clientes",
        interpretation=interpretation,
    )
