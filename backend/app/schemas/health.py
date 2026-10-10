"""Health check request and response schemas."""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class DatabaseHealth(BaseModel):
    """Database connectivity and state report."""

    connected: bool = Field(..., description="Whether database connection and ping succeeded")
    database_path: str = Field(..., description="Absolute path to the SQLite file")
    table_count: int = Field(..., description="Number of active user tables in the database")
    tables: List[str] = Field(default_factory=list, description="Names of verified tables")
    error: Optional[str] = Field(default=None, description="Error message if check failed")


class HealthCheckResponse(BaseModel):
    """System health check payload."""

    status: str = Field(..., description="'healthy' or 'degraded'")
    app_name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Runtime environment")
    debug: bool = Field(..., description="Debug mode indicator")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of check")
    database: DatabaseHealth = Field(..., description="Database health metrics")
    cors_allowed_origins: List[str] = Field(..., description="Allowed frontend CORS origins")
