"""Convenience runner script for the FastAPI backend application."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure backend directory is on sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import uvicorn
from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    print(f"Starting {settings.app_name} on http://{settings.host}:{settings.port}")
    print(f"Interactive Swagger documentation at: http://{settings.host}:{settings.port}/docs")
    print(f"Health check endpoint at: http://{settings.host}:{settings.port}/api/health")

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
