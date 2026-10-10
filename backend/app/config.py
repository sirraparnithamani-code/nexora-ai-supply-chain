"""Application configuration module.

Loads environment variables, defines paths, and provides typed application
settings with sensible defaults for local development.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List
from pydantic import BaseModel, ConfigDict, Field

# Base directories
BACKEND_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BACKEND_DIR.parent
DEFAULT_DATA_DIR = ROOT_DIR / "data"
DEFAULT_DB_PATH = DEFAULT_DATA_DIR / "supply_chain.db"

# Optional dotenv loading if python-dotenv is present
try:
    from dotenv import load_dotenv

    # Search for .env in backend/ or root directory
    env_paths = [BACKEND_DIR / ".env", ROOT_DIR / ".env"]
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            break
except ImportError:
    pass


def _parse_cors_origins(raw_origins: str | None) -> List[str]:
    """Parse CORS origins from environment variable (JSON array or comma-separated list)."""
    default_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    if not raw_origins:
        return default_origins

    raw_origins = raw_origins.strip()
    if raw_origins.startswith("[") and raw_origins.endswith("]"):
        try:
            parsed = json.loads(raw_origins)
            if isinstance(parsed, list):
                return [str(origin).strip() for origin in parsed if origin]
        except json.JSONDecodeError:
            pass

    # Split by comma
    origins = [item.strip() for item in raw_origins.split(",") if item.strip()]
    return origins if origins else default_origins


def _resolve_db_path(raw_path: str | None) -> Path:
    """Resolve database path relative to root/data directory if not absolute."""
    if not raw_path:
        return DEFAULT_DB_PATH

    path = Path(raw_path.strip())
    if not path.is_absolute():
        path = (BACKEND_DIR / path).resolve()
    return path


class Settings(BaseModel):
    """Application runtime settings."""

    app_name: str = Field(
        default="AI Agents for Resilient Supply Chain Manufacturing API",
        description="Public title for the API service",
    )
    version: str = Field(
        default="0.1.0",
        description="Semantic application version",
    )
    environment: str = Field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development"),
        description="Runtime environment (development, staging, production)",
    )
    debug: bool = Field(
        default_factory=lambda: os.getenv("DEBUG", "true").lower() in ("true", "1", "yes"),
        description="Debug mode toggle",
    )
    host: str = Field(
        default_factory=lambda: os.getenv("HOST", "127.0.0.1"),
        description="Server listening host",
    )
    port: int = Field(
        default_factory=lambda: int(os.getenv("PORT", "8000")),
        description="Server listening port",
    )
    database_path: Path = Field(
        default_factory=lambda: _resolve_db_path(os.getenv("DATABASE_PATH")),
        description="Filesystem path to the SQLite database file",
    )
    cors_origins: List[str] = Field(
        default_factory=lambda: _parse_cors_origins(os.getenv("CORS_ORIGINS")),
        description="List of allowed CORS origins for frontend communication",
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)


# Cached settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Return the application settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
