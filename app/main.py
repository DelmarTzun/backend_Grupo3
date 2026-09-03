from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import close_pool, create_pool
from app.routers import api_router
from app.routers.health import router as health_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    try:
        create_pool(settings)
        print(f"[Oracle] Pool creado -> {settings.dsn} (user={settings.oracle_user})")
    except Exception as exc:
        print(f"[Oracle] No se pudo crear el pool al iniciar: {exc}")
    yield
    close_pool()
    print("[Oracle] Pool cerrado")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="API Grupo 3: Oracle + FastAPI. Base lista para consultas y dashboard.",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(api_router)

    @app.get("/", tags=["raiz"])
    def root() -> dict:
        return {
            "app": settings.app_name,
            "docs": "/docs",
            "health": "/health?check_db=true",
            "tables": "/meta/tables",
            "ejemplo": "/api/clientes/top-monto",
        }

    return app


app = create_app()
