"""
Routers de la API.

Para agregar un dominio nuevo:
1. Crear app/services/<dominio>.py
2. Crear app/routers/<dominio>.py
3. Registrar abajo con include_router
"""

from fastapi import APIRouter

from app.routers import clientes, kpis, productos, tarjetas, tiempo

api_router = APIRouter(prefix="/api")

api_router.include_router(clientes.router, prefix="/clientes", tags=["clientes"])
api_router.include_router(tarjetas.router, prefix="/tarjetas", tags=["tarjetas"])
api_router.include_router(productos.router, prefix="/productos", tags=["productos"])
api_router.include_router(tiempo.router, prefix="/tiempo", tags=["tiempo"])
api_router.include_router(kpis.router, prefix="/kpis", tags=["kpis"])
