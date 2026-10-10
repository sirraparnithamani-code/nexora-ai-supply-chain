"""Unit tests for Demand Agent."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.agents.demand_agent import DemandAgent
from app.database import init_db
from app.schemas.agents import DemandAgentRequest


class DemandAgentTestCase(unittest.TestCase):
    """Test suite for Demand Agent forecasting, SLA risk, and input validation."""

    @classmethod
    def setUpClass(cls) -> None:
        init_db()
        cls.agent = DemandAgent()

    def test_nominal_7day_demand_forecast(self) -> None:
        """Verify baseline 7-day forecast generates daily forecasts with customer tier breakdown."""
        req = DemandAgentRequest(horizon_days=7, demand_change_pct=0.0)
        res = self.agent.run(req)

        self.assertEqual(res.agent_name, "Demand Agent")
        self.assertEqual(res.horizon_days, 7)
        self.assertGreater(res.total_units_demanded, 0)
        self.assertGreater(res.high_priority_gold_units, 0)
        self.assertIn("Non-ML", res.model_type)

        # Check daily forecast entries
        self.assertEqual(len(res.daily_forecasts), 14)  # 7 days * 2 products
        day_1_entries = [f for f in res.daily_forecasts if f.day == 1]
        self.assertEqual(len(day_1_entries), 2)

        for entry in day_1_entries:
            tiers = entry.customer_tier_breakdown
            self.assertIn("Gold", tiers)
            self.assertIn("Silver", tiers)
            self.assertIn("Standard", tiers)
            self.assertEqual(sum(tiers.values()), entry.forecasted_units)

    def test_demand_change_scenario_scaling(self) -> None:
        """Verify demand change percentage scales forecasted units up and down."""
        base_res = self.agent.run(DemandAgentRequest(horizon_days=7, demand_change_pct=0.0))
        surge_res = self.agent.run(DemandAgentRequest(horizon_days=7, demand_change_pct=25.0))
        drop_res = self.agent.run(DemandAgentRequest(horizon_days=7, demand_change_pct=-20.0))

        self.assertGreater(surge_res.total_units_demanded, base_res.total_units_demanded)
        self.assertLess(drop_res.total_units_demanded, base_res.total_units_demanded)

    def test_critical_sales_orders_and_penalties(self) -> None:
        """Verify exposure calculation for active sales order contracts and daily delay penalties."""
        req = DemandAgentRequest(horizon_days=7)
        res = self.agent.run(req)

        self.assertGreater(res.total_revenue_at_risk, 0.0)
        self.assertGreater(res.daily_sla_penalty_exposure, 0.0)
        self.assertTrue(len(res.critical_orders_at_risk) > 0)

        # First order in prioritized list should be Gold tier
        first_order = res.critical_orders_at_risk[0]
        self.assertEqual(first_order["customer_tier"], "Gold")

    def test_target_product_filter(self) -> None:
        """Verify forecast limits to specified target product."""
        req = DemandAgentRequest(horizon_days=7, target_products=["FG-ROBOT-01"])
        res = self.agent.run(req)

        for f in res.daily_forecasts:
            self.assertEqual(f.product_sku, "FG-ROBOT-01")

    def test_invalid_target_product_raises_error(self) -> None:
        """Verify unrecognized product SKU raises ValueError."""
        req = DemandAgentRequest(horizon_days=7, target_products=["NON-EXISTENT-SKU"])
        with self.assertRaises(ValueError) as ctx:
            self.agent.run(req)
        self.assertIn("not recognized", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
