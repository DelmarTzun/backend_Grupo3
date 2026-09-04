from fastapi import APIRouter

from app.services import tarjetas as svc

router = APIRouter()


@router.get("/marcas")
def marcas():
    return svc.marcas_resumen()


@router.get("/credito-vs-debito")
def credito_vs_debito():
    return svc.credito_vs_debito()


@router.get("/promedio-por-tipo")
def promedio_por_tipo():
    return svc.promedio_por_tipo()


@router.get("/clientes-multiples")
def clientes_multiples():
    return svc.clientes_multiples_tarjetas()
