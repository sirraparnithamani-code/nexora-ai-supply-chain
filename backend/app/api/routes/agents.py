"""API route handlers for NEXORA AI multi-agent endpoints.

Provides endpoints to execute individual specialized agents (Demand, Inventory,
Supplier-Risk, Logistics) and the comprehensive Coordinated Supply Chain Assessment.
"""

from __future__ import annotations

import logging
from typing import Any, Dict
from fastapi import APIRouter, HTTPException, status

from app.agents import (
    CoordinatorAgent,
    DemandAgent,
    InventoryAgent,
    LogisticsAgent,
    SupplierRiskAgent,
)
from app.schemas.agents import (
    CoordinatorAssessmentRequest,
    CoordinatorAssessmentResponse,
    DemandAgentRequest,
    DemandAgentResponse,
    InventoryAgentRequest,
    InventoryAgentResponse,
    LogisticsAgentRequest,
    LogisticsAgentResponse,
    SupplierRiskAgentRequest,
    SupplierRiskAgentResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["AI Agents"])

# Lazy-loaded agent instances
demand_agent = DemandAgent()
inventory_agent = InventoryAgent()
supplier_risk_agent = SupplierRiskAgent()
logistics_agent = LogisticsAgent()
coordinator_agent = CoordinatorAgent()


@router.get(
    "/info",
    summary="Agent Roster & Capabilities",
    description="Returns metadata, active status, and capabilities for all 4 domain agents and coordinator.",
)
async def get_agents_info() -> Dict[str, Any]:
    """Return active agent status and specialization capabilities."""
    return {
        "platform": "NEXORA AI",
        "governance_model": "Human-In-The-Loop Autonomous Multi-Agent System",
        "coordinator": {
            "name": "Coordinator Agent",
            "role": "Central multi-agent orchestrator & decision synthesizer",
            "status": "ONLINE",
            "permissions": [
                "EXECUTE_MULTI_AGENT_PIPELINE",
                "INVOKE_OR_TOOLS_SOLVER",
                "PROPOSE_ACTION_PLAN",
                "READ_AUDIT_LOGS",
            ],
            "governance_rule": "Proposal-Only: Cannot execute external financial transactions or PO commits without Human Planner Approval.",
            "inputs": [
                "shutdown_duration_days (int: 1-14)",
                "demand_change_pct (float: -50 to +50)",
                "disrupted_supplier_id (str)",
                "target_sku (str)",
                "alternate_capacity_factor (float: 0.0-1.0)",
                "available_inventory_override (int)",
                "logistics_delay_days (int: 0-7)",
            ],
            "outputs": [
                "assessment_id",
                "execution_pipeline",
                "shortages_identified",
                "risks_and_impacts",
                "recovery_options",
                "conflict_resolutions",
                "constraint_validations",
                "planning_approaches",
                "optimization_result",
                "confidence_score",
                "actionable_recommendations",
            ],
            "shared_data_schemas": [
                "CoordinatorAssessmentRequest",
                "CoordinatorAssessmentResponse",
                "ActionPlanItem",
                "OptimizationInput",
                "OptimizationResult",
            ],
        },
        "agents": [
            {
                "name": "Demand Agent",
                "role": "7-day demand forecasting, order prioritization, and contract SLA exposure",
                "endpoint": "/api/agents/demand",
                "status": "ONLINE",
                "permissions": [
                    "READ_SALES_ORDERS",
                    "READ_CONTRACT_SLAS",
                    "READ_HISTORICAL_DEMAND",
                ],
                "inputs": [
                    "horizon_days (int: 1-14)",
                    "demand_change_pct (float: -50 to +50)",
                    "target_products (optional list[str])",
                ],
                "outputs": [
                    "daily_forecasts",
                    "total_units_demanded",
                    "high_priority_gold_units",
                    "total_revenue_at_risk",
                    "daily_sla_penalty_exposure",
                    "critical_orders_at_risk",
                ],
                "shared_data_schemas": [
                    "DemandAgentRequest",
                    "DemandAgentResponse",
                    "DailyDemandForecast",
                ],
            },
            {
                "name": "Inventory Agent",
                "role": "Stock auditing, BOM explosion, safety stock runway, and shortage deficit",
                "endpoint": "/api/agents/inventory",
                "status": "ONLINE",
                "permissions": [
                    "READ_INVENTORY_LEVELS",
                    "READ_BOM",
                    "EXPLODE_BOM_REQUIREMENTS",
                ],
                "inputs": [
                    "target_sku (str)",
                    "horizon_days (int: 1-14)",
                    "daily_consumption_override (optional float)",
                    "initial_inventory_override (optional int)",
                ],
                "outputs": [
                    "current_on_hand_stock",
                    "safety_stock_threshold",
                    "daily_consumption_rate",
                    "runway_days",
                    "projected_stockout_day",
                    "production_requirements_units",
                    "net_shortage_units",
                    "daily_burn_down",
                    "affected_assembly_lines",
                    "bom_consumption_map",
                ],
                "shared_data_schemas": [
                    "InventoryAgentRequest",
                    "InventoryAgentResponse",
                    "DailyInventoryBurnDown",
                ],
            },
            {
                "name": "Supplier-Risk Agent",
                "role": "Supplier outage tracking, component impact, and alternative vendor capacity",
                "endpoint": "/api/agents/supplier-risk",
                "status": "ONLINE",
                "permissions": [
                    "READ_SUPPLIER_CATALOG",
                    "READ_SUPPLIER_RELIABILITY",
                    "CALCULATE_VENDOR_CAPACITY",
                ],
                "inputs": [
                    "disrupted_supplier_id (str)",
                    "shutdown_duration_days (int: 1-14)",
                    "affected_component_sku (str)",
                    "required_daily_deficit (optional float)",
                ],
                "outputs": [
                    "disrupted_supplier",
                    "alternative_suppliers",
                    "total_alternate_daily_capacity",
                    "can_cover_daily_deficit",
                    "capacity_surplus_deficit",
                    "risk_index",
                    "risk_level",
                    "recommended_suppliers",
                ],
                "shared_data_schemas": [
                    "SupplierRiskAgentRequest",
                    "SupplierRiskAgentResponse",
                    "AlternateSupplierSummary",
                ],
            },
            {
                "name": "Logistics Agent",
                "role": "Multi-modal freight lane evaluation, transit speed, and deadline feasibility",
                "endpoint": "/api/agents/logistics",
                "status": "ONLINE",
                "permissions": [
                    "READ_TRANSIT_LANES",
                    "READ_FREIGHT_RATES",
                    "EVALUATE_MODAL_SPLIT",
                ],
                "inputs": [
                    "target_destination (str)",
                    "required_delivery_day (int: 1-14)",
                    "total_units_to_ship (int)",
                    "unit_weight_kg (float)",
                    "logistics_delay_days (int: 0-7)",
                ],
                "outputs": [
                    "recommended_corridors",
                    "viable_modes_count",
                    "feasible_routes",
                    "fastest_route",
                    "cheapest_route",
                    "has_viable_deadline_route",
                    "estimated_total_freight_cost",
                ],
                "shared_data_schemas": [
                    "LogisticsAgentRequest",
                    "LogisticsAgentResponse",
                    "FreightRouteSummary",
                ],
            },
        ],
    }


@router.post(
    "/demand",
    response_model=DemandAgentResponse,
    summary="Run Demand Agent",
    description="Forecasts 7-day demand, evaluates customer priority tiers (Gold/Silver/Standard), and computes revenue at risk.",
)
async def run_demand_agent(request: DemandAgentRequest) -> DemandAgentResponse:
    """Execute the Demand Agent."""
    try:
        return demand_agent.run(request)
    except ValueError as val_err:
        logger.warning(f"Demand Agent invalid input: {val_err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        )
    except Exception as exc:
        logger.error(f"Demand Agent execution error: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Demand Agent error: {str(exc)}",
        )


@router.post(
    "/inventory",
    response_model=InventoryAgentResponse,
    summary="Run Inventory Agent",
    description="Performs BOM explosion, evaluates stock runway, and projects exact stockout date and net shortage.",
)
async def run_inventory_agent(request: InventoryAgentRequest) -> InventoryAgentResponse:
    """Execute the Inventory Agent."""
    try:
        return inventory_agent.run(request)
    except ValueError as val_err:
        logger.warning(f"Inventory Agent invalid input: {val_err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        )
    except Exception as exc:
        logger.error(f"Inventory Agent execution error: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inventory Agent error: {str(exc)}",
        )


@router.post(
    "/supplier-risk",
    response_model=SupplierRiskAgentResponse,
    summary="Run Supplier-Risk Agent",
    description="Evaluates critical supplier shutdown, assesses spare capacity of alternative suppliers, and calculates price premiums.",
)
async def run_supplier_risk_agent(request: SupplierRiskAgentRequest) -> SupplierRiskAgentResponse:
    """Execute the Supplier-Risk Agent."""
    try:
        return supplier_risk_agent.run(request)
    except ValueError as val_err:
        logger.warning(f"Supplier-Risk Agent invalid input: {val_err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        )
    except Exception as exc:
        logger.error(f"Supplier-Risk Agent execution error: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Supplier-Risk Agent error: {str(exc)}",
        )


@router.post(
    "/logistics",
    response_model=LogisticsAgentResponse,
    summary="Run Logistics Agent",
    description="Evaluates transit modes (Air, Expedited Truck, Sea) and identifies feasible routes beating the stockout deadline.",
)
async def run_logistics_agent(request: LogisticsAgentRequest) -> LogisticsAgentResponse:
    """Execute the Logistics Agent."""
    try:
        return logistics_agent.run(request)
    except ValueError as val_err:
        logger.warning(f"Logistics Agent invalid input: {val_err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        )
    except Exception as exc:
        logger.error(f"Logistics Agent execution error: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logistics Agent error: {str(exc)}",
        )


@router.post(
    "/coordinator",
    response_model=CoordinatorAssessmentResponse,
    summary="Run Coordinated Multi-Agent Assessment",
    description="Executes all four agents in sequence, synthesizes unified disruption assessment, and formulates actionable recovery plan.",
)
async def run_coordinator_assessment(
    request: CoordinatorAssessmentRequest,
) -> CoordinatorAssessmentResponse:
    """Execute full multi-agent coordinated assessment."""
    try:
        return coordinator_agent.run(request)
    except ValueError as val_err:
        logger.warning(f"Coordinator Agent invalid input: {val_err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        )
    except Exception as exc:
        logger.error(f"Coordinator Agent execution error: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Coordinator Agent error: {str(exc)}",
        )
