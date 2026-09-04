from fastapi import APIRouter
from app.schemas.dashboard import DashboardResponse

from app.services import tarjetas as svc

router = APIRouter()


@router.get("/marcas", response_model=DashboardResponse)
def marcas():
    return svc.marcas_resumen()


@router.get("/credito-vs-debito", response_model=DashboardResponse)
def credito_vs_debito():
    return svc.credito_vs_debito()


@router.get("/promedio-por-tipo", response_model=DashboardResponse)
def promedio_por_tipo():
    return svc.promedio_por_tipo()


@router.get("/clientes-multiples", response_model=DashboardResponse)
def clientes_multiples():
    return svc.clientes_multiples_tarjetas()
