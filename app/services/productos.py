"""
Servicio de productos y categorías — consultas SQL.

SQL Oracle puro (copiable a SQL Developer).
Tablas: TBL_PRODUCTOS, TBL_CATEGORIAS, TBL_DET_COMPRAS
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.database import fetch_all


from app.utils.responses import build_dashboard_response as _respuesta


def top_productos_cantidad() -> dict[str, Any]:
    """Top 10 productos por cantidad comprada."""
    sql = """
        SELECT *
        FROM (
            SELECT
                p.id_producto,
                p.nombre_producto,
                cat.nombre_categoria,
                SUM(d.cantidad) AS total_unidades,
                ROUND(SUM(d.subtotal), 2) AS ingresos_generados
            FROM tbl_det_compras d
            JOIN tbl_productos p ON p.id_producto = d.id_producto
            JOIN tbl_categorias cat ON cat.id_categoria = p.id_categoria
            GROUP BY p.id_producto, p.nombre_producto, cat.nombre_categoria
            ORDER BY total_unidades DESC
        )
        WHERE ROWNUM <= 10
    """
    data = fetch_all(sql)
    if data:
        top = data[0]
        interpretation = (
            f"'{top['nombre_producto']}' es el más consumido con "
            f"{int(top['total_unidades'])} unidades."
        )
    else:
        interpretation = "No hay ventas de productos."

    return _respuesta(
        question="¿Cuáles son los Top 10 productos por cantidad comprada?",
        data=data,
        unit="cantidad",
        interpretation=interpretation,
    )


def top_productos_ingresos() -> dict[str, Any]:
    """Top 10 productos por ingresos generados."""
    sql = """
        SELECT *
        FROM (
            SELECT
                p.id_producto,
                p.nombre_producto,
                cat.nombre_categoria,
                SUM(d.cantidad) AS total_unidades,
                ROUND(SUM(d.subtotal), 2) AS ingresos_generados
            FROM tbl_det_compras d
            JOIN tbl_productos p ON p.id_producto = d.id_producto
            JOIN tbl_categorias cat ON cat.id_categoria = p.id_categoria
            GROUP BY p.id_producto, p.nombre_producto, cat.nombre_categoria
            ORDER BY ingresos_generados DESC
        )
        WHERE ROWNUM <= 10
    """
    data = fetch_all(sql)
    if data:
        top = data[0]
        interpretation = (
            f"'{top['nombre_producto']}' lidera ingresos con "
            f"Q{top['ingresos_generados']:,.2f}."
        )
    else:
        interpretation = "No hay ventas de productos."

    return _respuesta(
        question="¿Cuáles son los Top 10 productos por ingresos generados?",
        data=data,
        unit="monto (Q) / unidades",
        interpretation=interpretation,
    )


def ventas_por_categoria() -> dict[str, Any]:
    """Ventas agregadas por categoría (mayor y menor al final de la lista)."""
    sql = """
        SELECT
            cat.id_categoria,
            cat.nombre_categoria,
            COUNT(DISTINCT d.id_compra) AS num_compras,
            SUM(d.cantidad) AS total_unidades,
            ROUND(SUM(d.subtotal), 2) AS monto_total
        FROM tbl_det_compras d
        JOIN tbl_productos p ON p.id_producto = d.id_producto
        JOIN tbl_categorias cat ON cat.id_categoria = p.id_categoria
        GROUP BY cat.id_categoria, cat.nombre_categoria
        ORDER BY monto_total DESC
    """
    data = fetch_all(sql)
    if data:
        interpretation = (
            f"Mayor venta: {data[0]['nombre_categoria']} "
            f"(Q{data[0]['monto_total']:,.2f}). "
            f"Menor venta: {data[-1]['nombre_categoria']} "
            f"(Q{data[-1]['monto_total']:,.2f})."
        )
    else:
        interpretation = "No hay ventas por categoría."

    return _respuesta(
        question="¿Cuáles son las categorías con mayor y menor monto de ventas?",
        data=data,
        unit="monto (Q)",
        interpretation=interpretation,
        extra={
            "mayor": data[0] if data else None,
            "menor": data[-1] if data else None,
        },
    )


def producto_top_por_categoria() -> dict[str, Any]:
    """Producto más vendido (por cantidad) dentro de cada categoría."""
    sql = """
        WITH RankedProductos AS (
            SELECT
                cat.id_categoria,
                cat.nombre_categoria,
                p.id_producto,
                p.nombre_producto,
                SUM(d.cantidad) AS total_vendido,
                ROUND(SUM(d.subtotal), 2) AS total_ingreso,
                RANK() OVER (
                    PARTITION BY cat.id_categoria
                    ORDER BY SUM(d.cantidad) DESC
                ) AS rank_en_categoria
            FROM tbl_det_compras d
            JOIN tbl_productos p ON p.id_producto = d.id_producto
            JOIN tbl_categorias cat ON cat.id_categoria = p.id_categoria
            GROUP BY
                cat.id_categoria, cat.nombre_categoria,
                p.id_producto, p.nombre_producto
        )
        SELECT
            id_categoria,
            nombre_categoria,
            id_producto,
            nombre_producto,
            total_vendido,
            total_ingreso,
            rank_en_categoria
        FROM RankedProductos
        WHERE rank_en_categoria = 1
        ORDER BY nombre_categoria
    """
    data = fetch_all(sql)
    return _respuesta(
        question="¿Cuál es el producto más vendido dentro de cada categoría (PARTITION BY)?",
        data=data,
        unit="cantidad",
        interpretation=(
            f"Se identificó el líder por unidades en {len(data)} categorías "
            "con RANK() PARTITION BY."
            if data
            else "Sin datos de ventas por categoría."
        ),
    )


def productos_sin_compras() -> dict[str, Any]:
    """Productos que nunca aparecen en un detalle de compra."""
    sql = """
        SELECT
            p.id_producto,
            p.nombre_producto,
            cat.nombre_categoria,
            p.precio_sugerido
        FROM tbl_productos p
        JOIN tbl_categorias cat ON cat.id_categoria = p.id_categoria
        WHERE NOT EXISTS (
            SELECT 1
            FROM tbl_det_compras d
            WHERE d.id_producto = p.id_producto
        )
        ORDER BY cat.nombre_categoria, p.nombre_producto
    """
    data = fetch_all(sql)
    return _respuesta(
        question="¿Qué productos nunca han sido comprados?",
        data=data,
        unit="productos",
        interpretation=(
            f"Hay {len(data)} producto(s) sin rotación."
            if data
            else "Todos los productos tienen al menos una venta."
        ),
    )


def precio_promedio_categoria() -> dict[str, Any]:
    """Precio promedio sugerido de productos por categoría."""
    sql = """
        SELECT
            cat.id_categoria,
            cat.nombre_categoria,
            COUNT(p.id_producto) AS num_productos,
            ROUND(AVG(p.precio_sugerido), 2) AS precio_promedio
        FROM tbl_categorias cat
        JOIN tbl_productos p ON p.id_categoria = cat.id_categoria
        GROUP BY cat.id_categoria, cat.nombre_categoria
        ORDER BY precio_promedio DESC
    """
    data = fetch_all(sql)
    if data:
        interpretation = (
            f"La categoría con precio promedio más alto es "
            f"{data[0]['nombre_categoria']} (Q{data[0]['precio_promedio']:,.2f})."
        )
    else:
        interpretation = "No hay productos por categoría."

    return _respuesta(
        question="¿Cuál es el precio promedio de productos por categoría?",
        data=data,
        unit="monto (Q)",
        interpretation=interpretation,
    )


def sobre_promedio_categoria() -> dict[str, Any]:
    """Productos cuyo precio sugerido supera el promedio de su categoría."""
    sql = """
        WITH promedio AS (
            SELECT
                id_categoria,
                AVG(precio_sugerido) AS precio_promedio
            FROM tbl_productos
            GROUP BY id_categoria
        )
        SELECT
            p.id_producto,
            p.nombre_producto,
            cat.nombre_categoria,
            p.precio_sugerido,
            ROUND(pr.precio_promedio, 2) AS precio_promedio_categoria,
            ROUND(p.precio_sugerido - pr.precio_promedio, 2) AS diferencia
        FROM tbl_productos p
        JOIN tbl_categorias cat ON cat.id_categoria = p.id_categoria
        JOIN promedio pr ON pr.id_categoria = p.id_categoria
        WHERE p.precio_sugerido > pr.precio_promedio
        ORDER BY diferencia DESC
    """
    data = fetch_all(sql)
    return _respuesta(
        question="¿Qué productos superan el precio promedio de su categoría?",
        data=data,
        unit="monto (Q)",
        interpretation=(
            f"{len(data)} productos están por encima del promedio de su categoría."
            if data
            else "Ningún producto supera el promedio de su categoría."
        ),
    )


def diferencia_precios() -> dict[str, Any]:
    """Diferencia entre PRECIO_SUGERIDO y PRECIO_UNITARIO de venta."""
    sql = """
        SELECT
            p.id_producto,
            p.nombre_producto,
            cat.nombre_categoria,
            p.precio_sugerido,
            ROUND(AVG(d.precio_unitario), 2) AS precio_unitario_promedio,
            ROUND(AVG(d.precio_unitario) - p.precio_sugerido, 2) AS diferencia_promedio,
            COUNT(*) AS veces_vendido
        FROM tbl_det_compras d
        JOIN tbl_productos p ON p.id_producto = d.id_producto
        JOIN tbl_categorias cat ON cat.id_categoria = p.id_categoria
        GROUP BY
            p.id_producto, p.nombre_producto,
            cat.nombre_categoria, p.precio_sugerido
        HAVING AVG(d.precio_unitario) <> p.precio_sugerido
        ORDER BY ABS(AVG(d.precio_unitario) - p.precio_sugerido) DESC
    """
    data = fetch_all(sql)
    return _respuesta(
        question="¿Hay diferencias entre PRECIO_SUGERIDO y PRECIO_UNITARIO?",
        data=data,
        unit="monto (Q)",
        interpretation=(
            f"Se detectaron {len(data)} productos con diferencia entre "
            "precio sugerido y precio unitario promedio de venta."
            if data
            else "No hay diferencias: el precio unitario coincide con el sugerido."
        ),
    )
