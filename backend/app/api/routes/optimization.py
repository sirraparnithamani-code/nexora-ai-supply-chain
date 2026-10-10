"""API route handlers for Google OR-Tools optimization engine.

Provides endpoints to run mathematical Mixed-Integer Linear Programming (MILP)
for supply chain disruption recovery and benchmark the three planning approaches.
"""

from __future__ import annotations

import logging
from typing import Any, Dict
from fastapi import APIRouter, HTTPException, status

from app.optimization.solver import OptimizationInput, OptimizationResult, OptimizationSolver

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/optimization", tags=["Optimization Engine"])

solver = OptimizationSolver()


@router.post(
    "/solve",
    response_model=OptimizationResult,
    summary="Solve Supply Chain Recovery MILP",
    description="Executes Google OR-Tools (SCIP) solver to compute optimal multi-sourcing recovery plan and benchmark against Baseline and Rule-Based approaches.",
)
async def solve_optimization(input_params: OptimizationInput) -> OptimizationResult:
    """Execute mathematical recovery optimization via Google OR-Tools."""
    try:
        return solver.solve(input_params)
    except Exception as exc:
        logger.error(f"Optimization solver execution error: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Optimization solver error: {str(exc)}",
        )
