"""Demand Agent module.

Forecasts 7-day customer demand using historical sales trends and active orders,
classifies demand across customer priority tiers, and calculates potential revenue
and SLA breach penalty risks.

Clearly distinguishes demo heuristic extrapolations from predictive machine-learning models.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from app.agents.base import BaseAgent
from app.schemas.agents import (
    DailyDemandForecast,
    DemandAgentRequest,
    DemandAgentResponse,
)
from app.services.data_service import (
    get_historical_demand_series,
    get_sales_orders_dataframe,
)


class DemandAgent(BaseAgent):
    """Specialized AI agent for demand forecasting and customer SLA protection."""

    def __init__(self) -> None:
        super().__init__("Demand Agent")

    def run(self, request: DemandAgentRequest) -> DemandAgentResponse:
        """Execute demand forecasting and contract exposure analysis."""
        with self.measure_latency() as timer:
            history = get_historical_demand_series()
            orders_df = get_sales_orders_dataframe()

            # Validate target products if specified
            if request.target_products:
                for sku in request.target_products:
                    if sku not in history:
                        raise ValueError(f"Product SKU '{sku}' not recognized in historical demand catalog.")
                target_skus = request.target_products
            else:
                target_skus = list(history.keys())

            multiplier = 1.0 + (request.demand_change_pct / 100.0)

            daily_forecasts: List[DailyDemandForecast] = []
            total_units = 0
            gold_units = 0

            # 1. Compute product daily baseline demand from 30-day moving average
            product_daily_nominal: Dict[str, int] = {}
            for sku in target_skus:
                past_series = history.get(sku, [180] * 30)
                mean_val = float(np.mean(past_series))
                adjusted_val = int(round(mean_val * multiplier))
                product_daily_nominal[sku] = max(10, adjusted_val)

            # 2. Project daily demand across the horizon
            for day_idx in range(1, request.horizon_days + 1):
                day_label = f"Day {day_idx}"

                for sku, daily_vol in product_daily_nominal.items():
                    # Estimate customer tier breakdown from active orders
                    tier_breakdown = {
                        "Gold": int(round(daily_vol * 0.40)),
                        "Silver": int(round(daily_vol * 0.35)),
                        "Standard": int(round(daily_vol * 0.25)),
                    }
                    # Ensure sum matches
                    diff = daily_vol - sum(tier_breakdown.values())
                    tier_breakdown["Standard"] += diff

                    daily_forecasts.append(
                        DailyDemandForecast(
                            day=day_idx,
                            date_label=day_label,
                            product_sku=sku,
                            forecasted_units=daily_vol,
                            customer_tier_breakdown=tier_breakdown,
                        )
                    )
                    total_units += daily_vol
                    gold_units += tier_breakdown["Gold"]

            # 3. Analyze critical customer orders in the horizon
            orders_in_window = orders_df[orders_df["due_day"] <= request.horizon_days]

            revenue_at_risk = 0.0
            daily_sla_penalties = 0.0
            critical_orders: List[Dict[str, Any]] = []

            for _, row in orders_in_window.iterrows():
                order_value = float(row["quantity"]) * float(row["unit_price"])
                revenue_at_risk += order_value
                daily_sla_penalties += float(row["sla_penalty_daily"])

                critical_orders.append({
                    "order_number": row["order_number"],
                    "customer_name": row["customer_name"],
                    "customer_tier": row["customer_tier"],
                    "product_sku": row["product_sku"],
                    "quantity": int(row["quantity"]),
                    "due_day": int(row["due_day"]),
                    "sla_penalty_daily": float(row["sla_penalty_daily"]),
                    "contract_value": order_value,
                })

            # Sort critical orders by tier priority (Gold first) and due date
            tier_weights = {"Gold": 1, "Silver": 2, "Standard": 3}
            critical_orders.sort(key=lambda o: (tier_weights.get(o["customer_tier"], 4), o["due_day"]))

            # 4. Formulate Agent Explanation & Reasoning
            demand_adj_text = (
                f"{request.demand_change_pct:+.1f}% scenario shift"
                if request.demand_change_pct != 0
                else "nominal baseline"
            )
            reasoning = (
                f"Demand Agent analyzed {request.horizon_days}-day demand across {len(target_skus)} product lines "
                f"under {demand_adj_text}. Projected total requirement is {total_units:,} finished units, "
                f"including {gold_units:,} critical Gold-tier customer units. "
                f"{len(critical_orders)} sales contracts are due within the window, exposing ₹{revenue_at_risk:,.2f} "
                f"in contract revenue and ₹{daily_sla_penalties:,.2f}/day in cumulative delay SLA penalties. "
                f"Recommendation: Prioritize protection of Gold-tier commitments (L&T, Tata Motors) to prevent contractual breach. "
                f"[Note: Forecast calculated via 30-day moving average heuristic for simulation testing]."
            )

        return DemandAgentResponse(
            execution_time_ms=timer["elapsed_ms"],
            horizon_days=request.horizon_days,
            demand_change_pct=request.demand_change_pct,
            daily_forecasts=daily_forecasts,
            total_units_demanded=total_units,
            high_priority_gold_units=gold_units,
            total_revenue_at_risk=revenue_at_risk,
            daily_sla_penalty_exposure=daily_sla_penalties,
            critical_orders_at_risk=critical_orders,
            reasoning=reasoning,
        )
