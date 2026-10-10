"""Unit tests for Inventory Agent."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.agents.inventory_agent import InventoryAgent
from app.database import init_db
from app.schemas.agents import InventoryAgentRequest


class InventoryAgentTestCase(unittest.TestCase):
    """Test suite for Inventory Agent stock runway, BOM explosion, and deficits."""

    @classmethod
    def setUpClass(cls) -> None:
        init_db()
        cls.agent = InventoryAgent()

    def test_stock_audit_and_bom_explosion(self) -> None:
        """Verify inventory audit resolves on-hand stock, safety stock, and BOM consumption rate."""
        req = InventoryAgentRequest(target_sku="CMP-MCU-9000", horizon_days=7)
        res = self.agent.run(req)

        self.assertEqual(res.agent_name, "Inventory Agent")
        self.assertEqual(res.target_sku, "CMP-MCU-9000")
        self.assertEqual(res.current_on_hand_stock, 2400)
        self.assertEqual(res.safety_stock_threshold, 600)
        self.assertGreater(res.daily_consumption_rate, 0)
        self.assertGreater(res.production_requirements_units, 0)
        self.assertIn("Non-ML", res.model_type)

        # BOM mapping must include products using MCU-9000
        self.assertIn("FG-ROBOT-01", res.bom_consumption_map)
        self.assertEqual(res.bom_consumption_map["FG-ROBOT-01"], 2)

    def test_runway_and_stockout_projection(self) -> None:
        """Verify stock runway calculation and projected stockout day."""
        req = InventoryAgentRequest(target_sku="CMP-MCU-9000", horizon_days=7)
        res = self.agent.run(req)

        self.assertAlmostEqual(res.runway_days, 2400 / res.daily_consumption_rate, places=1)
        self.assertIsNotNone(res.projected_stockout_day)
        self.assertGreaterEqual(res.projected_stockout_day, 1)
        self.assertLessEqual(res.projected_stockout_day, 7)

        # Check daily burn-down length matches horizon
        self.assertEqual(len(res.daily_burn_down), 7)
        last_day = res.daily_burn_down[-1]
        self.assertTrue(last_day.is_stockout or last_day.is_below_safety)

    def test_daily_consumption_override(self) -> None:
        """Verify consumption override influences runway and net shortage."""
        high_override = 1200.0
        req = InventoryAgentRequest(
            target_sku="CMP-MCU-9000",
            horizon_days=7,
            daily_consumption_override=high_override,
        )
        res = self.agent.run(req)

        self.assertEqual(res.daily_consumption_rate, high_override)
        self.assertEqual(res.production_requirements_units, 8400)
        self.assertEqual(res.net_shortage_units, 8400 - 2400)
        self.assertEqual(res.projected_stockout_day, 2)

    def test_invalid_sku_raises_error(self) -> None:
        """Verify requesting unknown component SKU raises descriptive ValueError."""
        req = InventoryAgentRequest(target_sku="NON-EXISTENT-PART", horizon_days=7)
        with self.assertRaises(ValueError) as ctx:
            self.agent.run(req)
        self.assertIn("not found in components catalog", str(ctx.exception))

    def test_negative_consumption_override_raises_error(self) -> None:
        """Verify negative daily consumption override raises ValueError."""
        req = InventoryAgentRequest(
            target_sku="CMP-MCU-9000",
            daily_consumption_override=-50.0,
        )
        with self.assertRaises(ValueError) as ctx:
            self.agent.run(req)
        self.assertIn("cannot be negative", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
