"""Health check route handlers."""

from __future__ import annotations

from datetime import datetime, timezone
from fastapi import APIRouter, Response, status

from app.config import get_settings
from app.database import check_db_health
from app.schemas.health import DatabaseHealth, HealthCheckResponse

router = APIRouter()


@router.get(
    "",
    response_model=HealthCheckResponse,
    summary="Application and Database Health Check",
    description="Inspects server uptime, environment settings, and SQLite database connectivity.",
)
async def get_health(response: Response) -> HealthCheckResponse:
    """Return health status of the application and its dependencies."""
    settings = get_settings()
    db_result = check_db_health()

    is_healthy = db_result["connected"]
    if not is_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    db_health = DatabaseHealth(
        connected=db_result["connected"],
        database_path=db_result["database_path"],
        table_count=db_result["table_count"],
        tables=db_result.get("tables", []),
        error=db_result.get("error"),
    )

    return HealthCheckResponse(
        status="healthy" if is_healthy else "degraded",
        app_name=settings.app_name,
        version=settings.version,
        environment=settings.environment,
        debug=settings.debug,
        timestamp=datetime.now(timezone.utc).isoformat(),
        database=db_health,
        cors_allowed_origins=settings.cors_origins,
    )


@router.get(
    "/ping",
    summary="Simple Liveness Ping",
    description="Ultra-fast liveness probe returning pong without database roundtrip.",
)
async def ping() -> dict[str, str]:
    """Return instant pong response."""
    return {"ping": "pong", "status": "ok"}
