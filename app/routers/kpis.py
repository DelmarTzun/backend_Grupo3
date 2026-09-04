from fastapi import APIRouter
from app.schemas.dashboard import DashboardResponse

from app.services import kpis as svc

router = APIRouter()


@router.get("/resumen", response_model=DashboardResponse)
def resumen():
    return svc.obtener_resumen_kpis()
