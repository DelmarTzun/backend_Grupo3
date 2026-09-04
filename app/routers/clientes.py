"""
EJEMPLO GUÍA — router de clientes.
Cada función del servicio se expone como endpoint REST.
"""

from fastapi import APIRouter
from app.schemas.dashboard import DashboardResponse

from app.services import clientes as svc

router = APIRouter()


@router.get("/top-monto", response_model=DashboardResponse)
def top_monto():
    return svc.top_por_monto()


@router.get("/top-compras", response_model=DashboardResponse)
def top_compras():
    return svc.top_por_compras()


@router.get("/ticket-promedio", response_model=DashboardResponse)
def ticket_promedio():
    return svc.ticket_promedio()


@router.get("/sin-compras", response_model=DashboardResponse)
def sin_compras():
    return svc.sin_compras()


@router.get("/sobre-promedio", response_model=DashboardResponse)
def sobre_promedio():
    return svc.sobre_promedio()


@router.get("/ranking", response_model=DashboardResponse)
def ranking():
    return svc.ranking_por_monto()
