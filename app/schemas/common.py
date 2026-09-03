from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"
    app: str
    env: str
    database: dict | None = None
