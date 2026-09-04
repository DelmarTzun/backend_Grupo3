from fastapi import APIRouter
from app.schemas.dashboard import DashboardResponse

from app.services import productos as svc

router = APIRouter()


@router.get("/top-cantidad", response_model=DashboardResponse)
def top_cantidad():
    return svc.top_productos_cantidad()


@router.get("/top-ingresos", response_model=DashboardResponse)
def top_ingresos():
    return svc.top_productos_ingresos()


@router.get("/categorias", response_model=DashboardResponse)
def categorias():
    return svc.ventas_por_categoria()


@router.get("/top-por-categoria", response_model=DashboardResponse)
def top_por_categoria():
    return svc.producto_top_por_categoria()


@router.get("/sin-compras", response_model=DashboardResponse)
def sin_compras():
    return svc.productos_sin_compras()


@router.get("/precio-promedio-categoria", response_model=DashboardResponse)
def precio_promedio_categoria():
    return svc.precio_promedio_categoria()


@router.get("/sobre-promedio-categoria", response_model=DashboardResponse)
def sobre_promedio_categoria():
    return svc.sobre_promedio_categoria()


@router.get("/diferencia-precios", response_model=DashboardResponse)
def diferencia_precios():
    return svc.diferencia_precios()
