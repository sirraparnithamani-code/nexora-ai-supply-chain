"""API routes package."""

from app.api.routes.agents import router as agents_router
from app.api.routes.approvals import router as approvals_router
from app.api.routes.data import router as data_router
from app.api.routes.health import router as health_router
from app.api.routes.optimization import router as optimization_router
from app.api.routes.simulator import router as simulator_router

__all__ = [
    "agents_router",
    "approvals_router",
    "data_router",
    "health_router",
    "optimization_router",
    "simulator_router",
]
