"""
EJEMPLO GUÍA — router de clientes.
Cada función del servicio se expone como endpoint REST.
"""

from fastapi import APIRouter

from app.services import clientes as svc

router = APIRouter()


@router.get("/top-monto")
def top_monto():
    return svc.top_por_monto()


@router.get("/sin-compras")
def sin_compras():
    return svc.sin_compras()


@router.get("/ranking")
def ranking():
    return svc.ranking_por_monto()
