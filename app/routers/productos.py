from fastapi import APIRouter

from app.services import productos as svc

router = APIRouter()


@router.get("/top-cantidad")
def top_cantidad():
    return svc.top_productos_cantidad()


@router.get("/top-ingresos")
def top_ingresos():
    return svc.top_productos_ingresos()


@router.get("/categorias")
def categorias():
    return svc.ventas_por_categoria()


@router.get("/top-por-categoria")
def top_por_categoria():
    return svc.producto_top_por_categoria()


@router.get("/sin-compras")
def sin_compras():
    return svc.productos_sin_compras()


@router.get("/precio-promedio-categoria")
def precio_promedio_categoria():
    return svc.precio_promedio_categoria()


@router.get("/sobre-promedio-categoria")
def sobre_promedio_categoria():
    return svc.sobre_promedio_categoria()


@router.get("/diferencia-precios")
def diferencia_precios():
    return svc.diferencia_precios()
