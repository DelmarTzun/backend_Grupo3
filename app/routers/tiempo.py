from fastapi import APIRouter

from app.services import tiempo as svc

router = APIRouter()


@router.get("/compras-por-mes")
def compras_por_mes():
    return svc.compras_por_mes()


@router.get("/ingresos-por-mes")
def ingresos_por_mes():
    return svc.ingresos_por_mes()


@router.get("/evolucion-mensual")
def evolucion_mensual():
    return svc.evolucion_mensual()


@router.get("/ranking-meses")
def ranking_meses():
    return svc.ranking_meses()
