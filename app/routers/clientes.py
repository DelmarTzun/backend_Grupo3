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


@router.get("/top-compras")
def top_compras():
    return svc.top_por_compras()


@router.get("/ticket-promedio")
def ticket_promedio():
    return svc.ticket_promedio()


@router.get("/sin-compras")
def sin_compras():
    return svc.sin_compras()


@router.get("/sobre-promedio")
def sobre_promedio():
    return svc.sobre_promedio()


@router.get("/ranking")
def ranking():
    return svc.ranking_por_monto()
