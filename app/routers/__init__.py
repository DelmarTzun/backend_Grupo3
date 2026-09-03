"""
Routers de la API.

Para agregar un dominio nuevo (ej. tarjetas):
1. Crear app/services/tarjetas.py
2. Crear app/routers/tarjetas.py
3. Registrar abajo con include_router
"""

from fastapi import APIRouter

from app.routers import clientes

api_router = APIRouter(prefix="/api")
api_router.include_router(clientes.router, prefix="/clientes", tags=["clientes"])
