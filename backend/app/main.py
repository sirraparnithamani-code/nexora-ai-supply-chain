"""Main FastAPI application entry point.

Configures lifespan startup/shutdown hooks, CORS middleware for the React frontend,
global error handling, and API routes.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import (
    agents_router,
    approvals_router,
    data_router,
    health_router,
    optimization_router,
    simulator_router,
)
from app.config import get_settings
from app.database import init_db

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("supply_chain_api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager for startup and shutdown events."""
    settings = get_settings()
    logger.info(f"Starting {settings.app_name} v{settings.version} in '{settings.environment}' mode")
    logger.info(f"Configured CORS origins: {settings.cors_origins}")

    # Initialize SQLite database and tables
    try:
        tables = init_db(settings.database_path)
        logger.info(f"SQLite database ready at {settings.database_path} with {len(tables)} tables")
    except Exception as exc:
        logger.error(f"Failed to initialize database during startup: {exc}", exc_info=True)

    yield

    logger.info("Application shutdown complete.")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description=(
            "Autonomous multi-agent platform for resilient manufacturing supply chain "
            "replanning, mathematical optimization with Google OR-Tools, and interactive what-if simulation."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # -------------------------------------------------------------------------
    # CORS Configuration for React Frontend
    # -------------------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -------------------------------------------------------------------------
    # Global Exception Handlers
    # -------------------------------------------------------------------------
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail,
                },
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(Exception)
    async def global_unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Unhandled error processing {request.method} {request.url.path}: {exc}", exc_info=True)
        detail = str(exc) if settings.debug else "An internal server error occurred."
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": 500,
                    "message": detail,
                },
                "path": str(request.url.path),
            },
        )

    # -------------------------------------------------------------------------
    # API Routers
    # -------------------------------------------------------------------------
    app.include_router(health_router, prefix="/api/health", tags=["Health"])
    # Convenience alias for top-level /health probes
    app.include_router(health_router, prefix="/health", include_in_schema=False)
    # Multi-Agent Intelligence routes
    app.include_router(agents_router, prefix="/api")
    # Mathematical Optimization routes (Google OR-Tools)
    app.include_router(optimization_router, prefix="/api")
    # What-If Simulator routes
    app.include_router(simulator_router, prefix="/api")
    # Human Planner Approvals & Governance routes
    app.include_router(approvals_router, prefix="/api")
    # Catalog & Operational Data routes
    app.include_router(data_router, prefix="/api")

    @app.get(
        "/",
        tags=["Root"],
        summary="API Root Information",
        description="Returns API status, links to interactive documentation, and project details.",
    )
    async def root() -> dict[str, object]:
        return {
            "name": settings.app_name,
            "version": settings.version,
            "status": "online",
            "documentation": {
                "swagger_ui": "/docs",
                "redoc": "/redoc",
                "openapi_spec": "/openapi.json",
            },
            "endpoints": {
                "health_check": "/api/health",
                "health_ping": "/api/health/ping",
                "agents_info": "/api/agents/info",
                "demand_agent": "/api/agents/demand",
                "inventory_agent": "/api/agents/inventory",
                "supplier_risk_agent": "/api/agents/supplier-risk",
                "logistics_agent": "/api/agents/logistics",
                "coordinator_agent": "/api/agents/coordinator",
                "optimization_solve": "/api/optimization/solve",
                "simulator_run": "/api/simulator/run",
                "approvals": "/api/approvals",
                "data_summary": "/api/data/summary",
            },
            "cors_allowed_origins": settings.cors_origins,
        }

    return app


# Application entry point for ASGI servers (e.g. uvicorn app.main:app)
app = create_app()
