"""Integration tests for FastAPI Multi-Agent REST API endpoints."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from starlette.testclient import TestClient

from app.database import init_db
from app.main import app


class AgentApiEndpointsTestCase(unittest.TestCase):
    """Test suite verifying FastAPI endpoints for individual agents and coordinator."""

    @classmethod
    def setUpClass(cls) -> None:
        init_db()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client.close()

    def test_get_agents_info(self) -> None:
        """Verify GET /api/agents/info returns 200 with all 4 domain agents online."""
        response = self.client.get("/api/agents/info")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["platform"], "NEXORA AI")
        self.assertEqual(data["coordinator"]["status"], "ONLINE")
        self.assertEqual(len(data["agents"]), 4)

    def test_post_demand_agent_success(self) -> None:
        """Verify POST /api/agents/demand returns 200 with forecast."""
        payload = {"horizon_days": 7, "demand_change_pct": 10.0}
        response = self.client.post("/api/agents/demand", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["agent_name"], "Demand Agent")
        self.assertEqual(data["horizon_days"], 7)
        self.assertGreater(data["total_units_demanded"], 0)

    def test_post_demand_agent_validation_error(self) -> None:
        """Verify POST /api/agents/demand returns 422 on out-of-bounds parameters."""
        payload = {"horizon_days": 99, "demand_change_pct": 100.0}  # Horizon must be <= 14, change <= 50
        response = self.client.post("/api/agents/demand", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_post_inventory_agent_success(self) -> None:
        """Verify POST /api/agents/inventory returns 200 with stock audit and burn down."""
        payload = {"target_sku": "CMP-MCU-9000", "horizon_days": 7}
        response = self.client.post("/api/agents/inventory", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["target_sku"], "CMP-MCU-9000")
        self.assertEqual(data["current_on_hand_stock"], 2400)
        self.assertGreater(data["production_requirements_units"], 0)

    def test_post_inventory_agent_invalid_sku(self) -> None:
        """Verify POST /api/agents/inventory returns 400 on unknown SKU."""
        payload = {"target_sku": "UNKNOWN_SKU_12345", "horizon_days": 7}
        response = self.client.post("/api/agents/inventory", json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        error_message = data.get("error", {}).get("message", "") or data.get("detail", "")
        self.assertIn("not found in components catalog", error_message)

    def test_post_supplier_risk_agent_success(self) -> None:
        """Verify POST /api/agents/supplier-risk returns 200 with supplier disruption details."""
        payload = {
            "disrupted_supplier_id": "SUP-001",
            "shutdown_duration_days": 7,
            "affected_component_sku": "CMP-MCU-9000",
            "required_daily_deficit": 580.0,
        }
        response = self.client.post("/api/agents/supplier-risk", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["agent_name"], "Supplier-Risk Agent")
        self.assertEqual(data["shutdown_duration_days"], 7)
        self.assertTrue(data["can_cover_daily_deficit"])

    def test_post_logistics_agent_success(self) -> None:
        """Verify POST /api/agents/logistics returns 200 with route evaluations."""
        payload = {
            "target_destination": "Assembly Plant 1 (Fremont, CA)",
            "required_delivery_day": 4,
            "total_units_to_ship": 850,
            "unit_weight_kg": 0.5,
        }
        response = self.client.post("/api/agents/logistics", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["agent_name"], "Logistics Agent")
        self.assertTrue(data["beats_stockout_deadline"])
        self.assertEqual(len(data["routes_evaluated"]), 4)

    def test_post_coordinator_assessment_success(self) -> None:
        """Verify POST /api/agents/coordinator executes full multi-agent synthesis."""
        payload = {
            "shutdown_duration_days": 7,
            "demand_change_pct": 0.0,
            "disrupted_supplier_id": "SUP-001",
            "target_sku": "CMP-MCU-9000",
            "alternate_capacity_factor": 1.0,
        }
        response = self.client.post("/api/agents/coordinator", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["project_name"], "NEXORA AI")
        self.assertEqual(len(data["execution_pipeline"]), 5)
        self.assertIn("shortages_identified", data)
        self.assertIn("risks_and_impacts", data)
        self.assertIn("recovery_options", data)
        self.assertEqual(data["approval_status"], "PENDING_APPROVAL")
        self.assertTrue(data["requires_human_approval"])


if __name__ == "__main__":
    unittest.main()
