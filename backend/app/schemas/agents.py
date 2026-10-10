"""Pydantic schemas for multi-agent supply chain intelligence.

Defines typed request and response contracts for the Demand Agent, Inventory Agent,
Supplier-Risk Agent, Logistics Agent, and Coordinator Agent.

Explicitly distinguishes demo heuristic calculations from predictive/machine-learning models.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ==============================================================================
# 1. DEMAND AGENT SCHEMAS
# ==============================================================================

class DailyDemandForecast(BaseModel):
    """Daily forecasted demand per product."""

    day: int = Field(..., description="Day number (1 to horizon)")
    date_label: str = Field(..., description="Human-readable day label (e.g. Day 1)")
    product_sku: str = Field(..., description="Finished product SKU")
    forecasted_units: int = Field(..., description="Projected units demanded")
    customer_tier_breakdown: Dict[str, int] = Field(
        default_factory=dict, description="Units demanded by Gold, Silver, Standard tiers"
    )


class DemandAgentRequest(BaseModel):
    """Request payload for the Demand Agent."""

    horizon_days: int = Field(default=7, ge=1, le=14, description="Forecast horizon in days")
    demand_change_pct: float = Field(
        default=0.0, ge=-50.0, le=50.0, description="Percentage adjustment to nominal demand"
    )
    target_products: Optional[List[str]] = Field(
        default=None, description="Optional filter of product SKUs to evaluate"
    )


class DemandAgentResponse(BaseModel):
    """Response payload from the Demand Agent."""

    agent_name: str = "Demand Agent"
    model_type: str = Field(
        default="Deterministic Moving-Average Extrapolation (Demo Heuristic — Non-ML)",
        description="Explicit classification of the computational model, distinguishing demo heuristics from ML models",
    )
    execution_time_ms: float
    horizon_days: int
    demand_change_pct: float
    daily_forecasts: List[DailyDemandForecast]
    total_units_demanded: int
    high_priority_gold_units: int
    total_revenue_at_risk: float
    daily_sla_penalty_exposure: float
    critical_orders_at_risk: List[Dict[str, Any]]
    methodology: str = (
        "Deterministic baseline forecast extrapolated from historical 30-day moving average "
        "and active sales order contracts, scaled by scenario parameters. "
        "(Note: Deterministic rule-based calculation, distinct from predictive neural/ML models)."
    )
    reasoning: str


# ==============================================================================
# 2. INVENTORY AGENT SCHEMAS
# ==============================================================================

class DailyInventoryBurnDown(BaseModel):
    """Day-by-day stock projection."""

    day: int
    opening_stock: int
    consumed_units: int
    closing_stock: int
    safety_stock_threshold: int
    is_below_safety: bool
    is_stockout: bool


class InventoryAgentRequest(BaseModel):
    """Request payload for the Inventory Agent."""

    target_sku: str = Field(default="CMP-MCU-9000", description="Component SKU under review")
    horizon_days: int = Field(default=7, ge=1, le=14, description="Projection horizon in days")
    daily_consumption_override: Optional[float] = Field(
        default=None, description="Optional override of daily component consumption rate"
    )
    initial_inventory_override: Optional[int] = Field(
        default=None, ge=0, description="Optional override of starting inventory units"
    )


class InventoryAgentResponse(BaseModel):
    """Response payload from the Inventory Agent."""

    agent_name: str = "Inventory Agent"
    model_type: str = Field(
        default="Deterministic BOM Explosion & Inventory Balance (Demo Heuristic — Non-ML)",
        description="Explicit classification of the computational model, distinguishing demo heuristics from ML models",
    )
    execution_time_ms: float
    target_sku: str
    target_component_name: str
    current_on_hand_stock: int
    safety_stock_threshold: int
    daily_consumption_rate: float
    runway_days: float
    projected_stockout_day: Optional[int]
    production_requirements_units: int = Field(
        ..., description="Total component units demanded by assembly lines over the projection horizon"
    )
    net_shortage_units: int
    daily_burn_down: List[DailyInventoryBurnDown]
    affected_assembly_lines: List[str]
    bom_consumption_map: Dict[str, int]
    reasoning: str


# ==============================================================================
# 3. SUPPLIER-RISK AGENT SCHEMAS
# ==============================================================================

class AlternateSupplierSummary(BaseModel):
    """Metrics and capabilities of a candidate alternate supplier."""

    supplier_id: str
    name: str
    tier: str
    location: str
    daily_capacity: int
    lead_time_days: int
    price_multiplier: float
    reliability_score: float
    estimated_unit_cost: float
    qualification_status: str


class SupplierRiskAgentRequest(BaseModel):
    """Request payload for the Supplier-Risk Agent."""

    disrupted_supplier_id: str = Field(default="SUP-001", description="Identifier of disrupted vendor")
    shutdown_duration_days: int = Field(default=7, ge=1, le=14, description="Outage duration in days")
    affected_component_sku: str = Field(default="CMP-MCU-9000", description="Component affected by outage")
    required_daily_deficit: Optional[float] = Field(
        default=580.0, description="Daily component deficit units that must be replenished"
    )


class SupplierRiskAgentResponse(BaseModel):
    """Response payload from the Supplier-Risk Agent."""

    agent_name: str = "Supplier-Risk Agent"
    model_type: str = Field(
        default="Deterministic Vendor Risk Scoring & Capacity Aggregation (Demo Heuristic — Non-ML)",
        description="Explicit classification of the computational model, distinguishing demo heuristics from ML models",
    )
    execution_time_ms: float
    disrupted_supplier: Dict[str, Any]
    shutdown_duration_days: int
    affected_component_sku: str
    affected_component_name: str = Field(
        default="Dual-Core Industrial Microcontroller",
        description="Name of component impacted by supplier shutdown",
    )
    alternative_suppliers: List[AlternateSupplierSummary]
    total_alternate_daily_capacity: int
    can_cover_daily_deficit: bool
    capacity_surplus_deficit: float
    risk_index: int
    risk_level: str
    recommended_suppliers: List[str]
    reasoning: str


# ==============================================================================
# 4. LOGISTICS AGENT SCHEMAS
# ==============================================================================

class FreightRouteSummary(BaseModel):
    """Transit lane speed, cost, and deadline feasibility evaluation."""

    route_id: str
    origin: str
    destination: str
    mode: str
    transit_days: int
    cost_per_kg: float
    total_freight_cost: float
    arrival_day: int
    meets_deadline: bool
    delay_days_vs_deadline: int = Field(
        default=0, description="Days delayed beyond required arrival deadline (0 if on-time)"
    )
    reliability_score: float
    carrier: str


class LogisticsAgentRequest(BaseModel):
    """Request payload for the Logistics Agent."""

    target_destination: str = Field(
        default="Assembly Plant 1 (Hyderabad Plant / Cherlapally)", description="Receiving manufacturing facility"
    )
    required_delivery_day: int = Field(
        default=4, ge=1, le=14, description="Target arrival day before inventory stockout"
    )
    total_units_to_ship: int = Field(
        default=850, ge=1, description="Quantity of replacement components to transport"
    )
    unit_weight_kg: float = Field(
        default=0.5, gt=0, description="Weight per component unit in kilograms"
    )
    logistics_delay_days: int = Field(
        default=0, ge=0, le=7, description="Optional logistics delay added to transit corridors"
    )


class LogisticsAgentResponse(BaseModel):
    """Response payload from the Logistics Agent."""

    agent_name: str = "Logistics Agent"
    model_type: str = Field(
        default="Multi-Modal Transit & Freight Cost Evaluation (Demo Heuristic — Non-ML)",
        description="Explicit classification of the computational model, distinguishing demo heuristics from ML models",
    )
    execution_time_ms: float
    routes_evaluated: List[FreightRouteSummary]
    recommended_mode: str
    fastest_eta_days: int
    beats_stockout_deadline: bool
    estimated_delay_days: int = Field(
        default=0, description="Estimated delay of recommended transit option (0 if beats deadline)"
    )
    feasible_routes_count: int = Field(
        default=0, description="Number of transit corridors capable of beating the stockout deadline"
    )
    estimated_transport_cost: float
    split_freight_plan: Dict[str, Any]
    reasoning: str


# ==============================================================================
# 5. COORDINATOR AGENT SCHEMAS
# ==============================================================================

class ActionPlanItem(BaseModel):
    """Line-item mitigation action recommended by the Coordinator."""

    action_type: str
    entity_target: str
    quantity_units: int
    mode: str
    arrival_day: int
    estimated_cost: float
    rationale: str


class CoordinatorAssessmentRequest(BaseModel):
    """Request payload for the complete Coordinated Supply Chain Assessment."""

    shutdown_duration_days: int = Field(default=7, ge=1, le=14, description="Outage duration in days")
    demand_change_pct: float = Field(
        default=0.0, ge=-50.0, le=50.0, description="Customer demand change adjustment percentage"
    )
    disrupted_supplier_id: str = Field(default="SUP-001", description="Disrupted primary supplier ID")
    target_sku: str = Field(default="CMP-MCU-9000", description="Critical component SKU")
    alternate_capacity_factor: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Availability multiplier on alternate supplier capacities"
    )
    available_inventory_override: Optional[int] = Field(
        default=None, ge=0, description="Optional override of starting inventory units"
    )
    logistics_delay_days: int = Field(
        default=0, ge=0, le=7, description="Optional logistics delay added to freight transit times"
    )


class CoordinatorAssessmentResponse(BaseModel):
    """Unified assessment payload synthesized by the Coordinator Agent."""

    assessment_id: str
    timestamp: str
    project_name: str = "NEXORA AI"
    model_type: str = Field(
        default="Multi-Agent Coordination & Google OR-Tools MILP Optimization (Deterministic Non-ML Engine)",
        description="Explicit classification of the computational model",
    )
    methodology: str = (
        "Multi-agent coordination sequencing Demand, Inventory, Supplier-Risk, and Logistics agents, "
        "integrated with Google OR-Tools Mixed-Integer Linear Programming (MILP SCIP) to benchmark "
        "Baseline, Rule-Based, and Optimal recovery strategies."
    )
    summary: str
    execution_pipeline: List[str]
    total_pipeline_time_ms: float
    demand_assessment: DemandAgentResponse
    inventory_assessment: InventoryAgentResponse
    supplier_risk_assessment: SupplierRiskAgentResponse
    logistics_assessment: LogisticsAgentResponse
    shortages_identified: Dict[str, Any]
    risks_and_impacts: Dict[str, Any]
    recovery_options: List[ActionPlanItem]
    estimated_total_mitigation_cost: float
    projected_fulfillment_rate: float
    requires_human_approval: bool = True
    approval_status: str = "PENDING_APPROVAL"
    actionable_recommendations: List[str]
    planning_approaches: Optional[List[Dict[str, Any]]] = None
    optimization_result: Optional[Dict[str, Any]] = None
    solver_status: Optional[str] = None
    solver_runtime_ms: Optional[float] = None
    is_optimal: Optional[bool] = None
    conflict_resolutions: List[Dict[str, Any]] = Field(default_factory=list)
    constraint_validations: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_score: float = Field(default=96.4, description="Calculated confidence percentage of recovery plan")
    confidence_rationale: str = Field(
        default="Mathematically verified optimal dual-sourcing allocation synthesized by Google OR-Tools SCIP solver.",
        description="Operational justification for the confidence rating",
    )
    governance_details: Dict[str, Any] = Field(default_factory=dict)

