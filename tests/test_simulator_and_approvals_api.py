"""Tests for What-If Simulator API, Planner Approvals Workflow, and Persistence.

Validates:
1. POST /api/simulator/run with dynamic parameter permutations.
2. GET /api/approvals returns pending decisions and SQLite audit log history.
3. POST /api/approvals/{id}/decide authorizes or rejects actions and persists to SQLite.
4. POST /api/approvals/reset restores the pending review queue.
5. POST /api/optimization/solve returns direct OR-Tools mathematical solution.
"""

from __future__ import annotations

import unittest
from starlette.testclient import TestClient

from app.main import app


class SimulatorAndApprovalsApiTestCase(unittest.TestCase):
    """Integration test suite for Simulator, Approvals, and Optimization APIs."""

    def setUp(self) -> None:
        """Create TestClient instance."""
        self.client = TestClient(app)

    def test_post_simulator_run_default_parameters(self) -> None:
        """POST /api/simulator/run with default parameters returns 200 and valid schema."""
        payload = {
            "duration": 7,
            "demand_change": 0.0,
            "alternate_capacity": 65.0,
            "available_inventory": 2400,
            "logistics_delay": 0,
        }

        response = self.client.post("/api/simulator/run", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("kpis", data)
        self.assertIn("comparison_data", data)
        self.assertIn("planning_approaches", data)
        self.assertIn("seven_day_trajectory", data)
        self.assertIn("solver_status", data)
        self.assertEqual(data["solver_status"], "OPTIMAL")
        self.assertTrue(data["is_optimal"])
        self.assertGreater(len(data["kpis"]), 3)
        self.assertEqual(len(data["planning_approaches"]), 3)
        self.assertEqual(len(data["seven_day_trajectory"]), 7)

    def test_post_simulator_run_extreme_stress_scenario(self) -> None:
        """POST /api/simulator/run under 14-day shutdown, +30% demand, depleted inventory."""
        payload = {
            "duration": 14,
            "demand_change": 30.0,
            "alternate_capacity": 30.0,
            "available_inventory": 800,
            "logistics_delay": 3,
        }

        response = self.client.post("/api/simulator/run", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["scenario_params"]["duration"], 14)
        self.assertEqual(data["scenario_params"]["demand_change"], 30.0)
        self.assertIsNotNone(data["solver_runtime_ms"])

    def test_get_approvals_list_and_audit_history(self) -> None:
        """GET /api/approvals returns approval items and SQLite audit logs."""
        response = self.client.get("/api/approvals")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("approvals", data)
        self.assertIn("audit_logs", data)
        self.assertIn("pending_count", data)
        self.assertIn("approved_total_commitment", data)
        self.assertGreaterEqual(len(data["approvals"]), 3)
        self.assertGreaterEqual(len(data["audit_logs"]), 1)

    def test_post_approval_decision_persists_to_sqlite(self) -> None:
        """POST /api/approvals/{id}/decide updates decision status and logs to SQLite."""
        # Authorize PO-8821
        decision_payload = {
            "decision": "APPROVED",
            "notes": "Emergency air freight authorized under contingency policy.",
            "planner_name": "R. Verma (Lead Operations Planner)",
        }

        res = self.client.post("/api/approvals/PO-8821/decide", json=decision_payload)
        self.assertEqual(res.status_code, 200)

        data = res.json()
        self.assertEqual(data["approval"]["status"], "APPROVED")
        self.assertIn("audit_record", data)
        self.assertEqual(data["audit_record"]["action"], "APPROVED")

        # Verify change persists in subsequent GET
        get_res = self.client.get("/api/approvals")
        self.assertEqual(get_res.status_code, 200)
        updated_items = get_res.json()["approvals"]
        matching_item = next(item for item in updated_items if item["id"] == "PO-8821")
        self.assertEqual(matching_item["status"], "APPROVED")

    def test_post_approval_rejection_decision(self) -> None:
        """POST /api/approvals/{id}/decide supports REJECTED status."""
        payload = {
            "decision": "REJECTED",
            "notes": "Declined due to budget review.",
            "planner_name": "R. Verma (Lead Operations Planner)",
        }

        res = self.client.post("/api/approvals/PO-8822/decide", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["approval"]["status"], "REJECTED")

    def test_post_approval_invalid_id_returns_404(self) -> None:
        """Attempting to decide on non-existent order ID returns 404."""
        payload = {
            "decision": "APPROVED",
            "notes": "Invalid test",
        }
        res = self.client.post("/api/approvals/PO-NONEXISTENT/decide", json=payload)
        self.assertEqual(res.status_code, 404)

    def test_post_approvals_reset(self) -> None:
        """POST /api/approvals/reset restores pending state and logs reset action."""
        res = self.client.post("/api/approvals/reset")
        self.assertEqual(res.status_code, 200)

        get_res = self.client.get("/api/approvals")
        self.assertEqual(get_res.status_code, 200)
        approvals = get_res.json()["approvals"]
        for item in approvals:
            self.assertEqual(item["status"], "PENDING")

    def test_post_optimization_solve_direct_endpoint(self) -> None:
        """POST /api/optimization/solve executes OR-Tools solver directly."""
        payload = {
            "horizon_days": 7,
            "shutdown_duration_days": 7,
            "initial_inventory": 2400,
            "safety_stock_threshold": 600,
            "daily_consumption_rate": 580.0,
            "demand_change_pct": 0.0,
            "alternate_capacity_factor": 0.65,
            "logistics_delay_days": 0,
            "target_sku": "CMP-MCU-9000",
            "disrupted_supplier_id": "SUP-001",
        }

        res = self.client.post("/api/optimization/solve", json=payload)
        self.assertEqual(res.status_code, 200)

        data = res.json()
        self.assertEqual(data["solver_status"], "OPTIMAL")
        self.assertTrue(data["is_optimal"])
        self.assertIn("baseline_plan", data)
        self.assertIn("heuristic_plan", data)
        self.assertIn("optimized_plan", data)
        self.assertGreater(len(data["decision_allocations"]), 0)


if __name__ == "__main__":
    unittest.main()
