"""Unit tests for Logistics Agent."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.agents.logistics_agent import LogisticsAgent
from app.schemas.agents import LogisticsAgentRequest


class LogisticsAgentTestCase(unittest.TestCase):
    """Test suite for Logistics Agent freight routing, transit delays, and multi-modal optimization."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.agent = LogisticsAgent()

    def test_multi_modal_route_evaluation(self) -> None:
        """Verify comparison across Air Cargo, Expedited Truck, and Ocean Freight."""
        req = LogisticsAgentRequest(
            target_destination="Assembly Plant 1 (Fremont, CA)",
            required_delivery_day=4,
            total_units_to_ship=850,
            unit_weight_kg=0.5,
        )
        res = self.agent.run(req)

        self.assertEqual(res.agent_name, "Logistics Agent")
        self.assertEqual(len(res.routes_evaluated), 4)
        self.assertTrue(res.beats_stockout_deadline)
        self.assertEqual(res.fastest_eta_days, 3)
        self.assertEqual(res.estimated_delay_days, 0)
        self.assertGreaterEqual(res.feasible_routes_count, 1)
        self.assertIn("Non-ML", res.model_type)

        # Check ocean freight delay
        ocean_route = next(r for r in res.routes_evaluated if "Ocean" in r.mode)
        self.assertFalse(ocean_route.meets_deadline)
        self.assertEqual(ocean_route.delay_days_vs_deadline, 19 - 4)  # 15 days delay

        # Check air cargo meets deadline
        air_route = next(r for r in res.routes_evaluated if "Air Cargo" in r.mode)
        self.assertTrue(air_route.meets_deadline)
        self.assertEqual(air_route.delay_days_vs_deadline, 0)

    def test_dual_modal_split_routing_plan(self) -> None:
        """Verify dual-modal split strategy separates urgent air batch from secondary ground."""
        req = LogisticsAgentRequest(
            required_delivery_day=4,
            total_units_to_ship=850,
            unit_weight_kg=0.5,
        )
        res = self.agent.run(req)

        plan = res.split_freight_plan
        self.assertEqual(plan["strategy"], "Dual-Modal Split Routing")
        self.assertEqual(plan["emergency_air_units"], 500)
        self.assertEqual(plan["secondary_ground_units"], 350)
        self.assertGreater(plan["cost_savings_vs_all_air"], 0.0)

    def test_tight_deadline_only_air_feasible(self) -> None:
        """Verify tight Day 3 deadline filters out slower ground and ocean routes."""
        req = LogisticsAgentRequest(
            required_delivery_day=3,
            total_units_to_ship=500,
            unit_weight_kg=0.5,
        )
        res = self.agent.run(req)

        self.assertTrue(res.beats_stockout_deadline)
        feasible_modes = [r.mode for r in res.routes_evaluated if r.meets_deadline]
        self.assertIn("Dedicated Air Cargo Charter", feasible_modes)
        self.assertNotIn("Standard Transpacific Ocean Freight", feasible_modes)

    def test_invalid_negative_inputs_raise_errors(self) -> None:
        """Verify negative unit weights or delivery days raise ValueError."""
        with self.assertRaises(ValueError):
            self.agent.run(LogisticsAgentRequest(unit_weight_kg=-1.0))

        with self.assertRaises(ValueError):
            self.agent.run(LogisticsAgentRequest(required_delivery_day=-2))


if __name__ == "__main__":
    unittest.main()
