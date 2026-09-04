from fastapi import APIRouter
from app.schemas.dashboard import DashboardResponse

from app.services import tiempo as svc

router = APIRouter()


@router.get("/compras-por-mes", response_model=DashboardResponse)
def compras_por_mes():
    return svc.compras_por_mes()


@router.get("/ingresos-por-mes", response_model=DashboardResponse)
def ingresos_por_mes():
    return svc.ingresos_por_mes()


@router.get("/evolucion-mensual", response_model=DashboardResponse)
def evolucion_mensual():
    return svc.evolucion_mensual()


@router.get("/ranking-meses", response_model=DashboardResponse)
def ranking_meses():
    return svc.ranking_meses()
