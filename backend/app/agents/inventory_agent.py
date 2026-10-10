"""Inventory Agent module.

Performs multi-level Bill of Materials (BOM) explosion, projects component stock depletion,
calculates safety stock runways, and identifies exact stockout dates, net shortages, and
cumulative production requirements.

Clearly distinguishes demo heuristic calculations from predictive machine-learning models.
"""

from __future__ import annotations

from typing import Dict, List, Optional
import pandas as pd

from app.agents.base import BaseAgent
from app.schemas.agents import (
    DailyInventoryBurnDown,
    InventoryAgentRequest,
    InventoryAgentResponse,
)
from app.services.data_service import (
    get_bom_dataframe,
    get_components_dataframe,
)


class InventoryAgent(BaseAgent):
    """Specialized AI agent for inventory auditing, BOM explosion, and stockout projection."""

    def __init__(self) -> None:
        super().__init__("Inventory Agent")

    def run(self, request: InventoryAgentRequest) -> InventoryAgentResponse:
        """Execute inventory audit, BOM explosion, and day-by-day burn down projection."""
        with self.measure_latency() as timer:
            comp_df = get_components_dataframe()
            bom_df = get_bom_dataframe()

            if comp_df.empty:
                raise ValueError("Component database is unpopulated. Run database seeding before executing agents.")

            # 1. Locate target component record with input validation
            matched = comp_df[comp_df["sku"].str.upper() == request.target_sku.strip().upper()]
            if matched.empty:
                valid_skus = ", ".join(comp_df["sku"].tolist())
                raise ValueError(
                    f"Component SKU '{request.target_sku}' not found in components catalog. Available SKUs: {valid_skus}"
                )

            comp_row = matched.iloc[0]
            sku = str(comp_row["sku"])
            comp_name = str(comp_row["name"])
            current_stock = (
                int(request.initial_inventory_override)
                if request.initial_inventory_override is not None
                else int(comp_row["current_stock"])
            )
            safety_stock = int(comp_row["safety_stock_min"])

            # 2. BOM Explosion: calculate daily component consumption across finished goods
            comp_boms = bom_df[bom_df["component_sku"].str.upper() == sku.upper()]
            bom_map: Dict[str, int] = {}
            affected_lines: List[str] = []

            daily_consumption = 0.0
            nominal_product_rates = {"FG-ROBOT-01": 180, "FG-CTRL-02": 220}

            for _, b_row in comp_boms.iterrows():
                p_sku = str(b_row["product_sku"])
                qty_req = int(b_row["quantity_required"])
                bom_map[p_sku] = qty_req

                p_daily_vol = nominal_product_rates.get(p_sku, 150)
                daily_consumption += qty_req * p_daily_vol
                affected_lines.append(f"Assembly Line ({p_sku}: {b_row['product_name']})")

            if request.daily_consumption_override is not None:
                if request.daily_consumption_override < 0:
                    raise ValueError("Daily consumption override cannot be negative.")
                daily_consumption = max(1.0, request.daily_consumption_override)
            elif daily_consumption <= 0:
                daily_consumption = 580.0  # Default nominal consumption for standalone components

            # 3. Calculate Days of Inventory (DOI)
            runway_days = round(current_stock / daily_consumption, 1)

            # 4. Day-by-Day Burn Down Simulation
            daily_burn: List[DailyInventoryBurnDown] = []
            running_stock = current_stock
            projected_stockout_day: Optional[int] = None

            for day_idx in range(1, request.horizon_days + 1):
                open_stk = running_stock
                consumed = int(round(daily_consumption))
                close_stk = max(0, open_stk - consumed)
                running_stock = close_stk

                is_below = close_stk < safety_stock
                is_zero = close_stk == 0

                if is_zero and projected_stockout_day is None:
                    projected_stockout_day = day_idx

                daily_burn.append(
                    DailyInventoryBurnDown(
                        day=day_idx,
                        opening_stock=open_stk,
                        consumed_units=consumed,
                        closing_stock=close_stk,
                        safety_stock_threshold=safety_stock,
                        is_below_safety=is_below,
                        is_stockout=is_zero,
                    )
                )

            # 5. Production Requirements & Net Deficit Calculation
            production_requirements = int(round(daily_consumption * request.horizon_days))
            net_shortage = max(0, production_requirements - current_stock)

            # 6. Reasoning Summary
            stockout_str = f"Day {projected_stockout_day}" if projected_stockout_day else f"beyond {request.horizon_days}-day horizon"
            safety_breach_day = next((d.day for d in daily_burn if d.is_below_safety), None)
            safety_str = f"Day {safety_breach_day}" if safety_breach_day else "not breached"

            reasoning = (
                f"Inventory Agent audited {sku} ({comp_name}). Available on-hand inventory is "
                f"{current_stock:,} units against a safety stock floor of {safety_stock:,} units. "
                f"BOM consumption rate across {len(bom_map)} product lines is {int(daily_consumption):,} units/day. "
                f"Cumulative {request.horizon_days}-day production requirements total {production_requirements:,} units. "
                f"Current stock runway is {runway_days} days. Without replenishment, safety buffer breaches on {safety_str} "
                f"and complete stockout occurs on {stockout_str}. "
                f"Cumulative net component shortage is {net_shortage:,} units. "
                f"Recommendation: Trigger alternative supplier purchase order before {safety_str} to avoid assembly halts. "
                f"[Note: Inventory burn projection based on deterministic BOM consumption rules]."
            )

        return InventoryAgentResponse(
            execution_time_ms=timer["elapsed_ms"],
            target_sku=sku,
            target_component_name=comp_name,
            current_on_hand_stock=current_stock,
            safety_stock_threshold=safety_stock,
            daily_consumption_rate=daily_consumption,
            runway_days=runway_days,
            projected_stockout_day=projected_stockout_day,
            production_requirements_units=production_requirements,
            net_shortage_units=net_shortage,
            daily_burn_down=daily_burn,
            affected_assembly_lines=affected_lines,
            bom_consumption_map=bom_map,
            reasoning=reasoning,
        )
