from fastapi import APIRouter

from app.services import kpis as svc

router = APIRouter()


@router.get("/resumen")
def resumen():
    return svc.obtener_resumen_kpis()
