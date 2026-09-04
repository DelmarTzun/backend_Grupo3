from typing import Any

from pydantic import BaseModel, Field


class DashboardResponse(BaseModel):
    question: str = Field(..., description="La pregunta de negocio respondida por este endpoint")
    interpretation: str = Field(..., description="Interpretación amigable de los datos obtenidos")
    unit: str = Field(..., description="Unidad de medida de los datos principales (ej. monto (Q), compras, clientes)")
    source: str = Field(..., description="Origen de los datos, por defecto Oracle Database")
    analyzed_at: str = Field(..., description="Fecha y hora de la consulta (ISO 8601)")
    data: list[dict[str, Any]] | dict[str, Any] = Field(..., description="Datos crudos obtenidos de la base de datos")
    extra: dict[str, Any] | None = Field(default=None, description="Datos adicionales opcionales")


class ErrorResponse(BaseModel):
    status: str = Field(default="error", description="Estado de la respuesta")
    message: str = Field(..., description="Mensaje detallado del error")
