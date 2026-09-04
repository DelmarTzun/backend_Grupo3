from datetime import datetime, timezone
from typing import Any

from app.schemas.dashboard import DashboardResponse


def build_dashboard_response(
    *,
    question: str,
    data: Any,
    unit: str,
    interpretation: str,
    extra: dict[str, Any] | None = None,
) -> DashboardResponse:
    """
    Formato común y estandarizado de respuesta para el dashboard / presentación.
    """
    return DashboardResponse(
        question=question,
        interpretation=interpretation,
        unit=unit,
        source="Oracle Database · esquema DBA_COMPRAS",
        analyzed_at=datetime.now(timezone.utc).isoformat(),
        data=data,
        extra=extra,
    )
