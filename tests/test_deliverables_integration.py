"""Integration and unit tests for Deliverables 1-7 enhancements.

Validates:
1. Data quality checks and documented cost assumptions (Deliverables 1 & 7).
2. Agent roster with defined inputs, outputs, permissions, and shared schemas (Deliverable 2).
3. Coordinator conflict resolutions, constraint validations, and governance gate (Deliverable 3).
4. OR-Tools solver with all 8 Deliverable 6 evaluation metrics (fill rate, backorders, landed cost,
   recovery time, inventory days, constraint violations, runtime, recommendation stability).
5. Governance analysis policy and compliance metrics (Deliverable 7).
"""

from __future__ import annotations

import unittest
from starlette.testclient import TestClient

from app.main import app
from app.optimization.solver import OptimizationInput, OptimizationResult, OptimizationSolver
from app.services.data_service import get_cost_assumptions, run_data_quality_checks


class DeliverablesIntegrationTestCase(unittest.TestCase):
    """Test suite for Deliverables 1-7 capabilities."""

    def setUp(self) -> None:
        """Create TestClient instance."""
        self.client = TestClient(app)
        self.solver = OptimizationSolver()

    def test_data_quality_checks_and_endpoint(self) -> None:
        """Verify automated data quality audit returns HEALTHY with all checks passed."""
        # Direct service call
        report = run_data_quality_checks()
        self.assertEqual(report["status"], "HEALTHY")
        self.assertGreaterEqual(report["total_checks"], 6)
        self.assertEqual(report["failed_checks"], 0)
        self.assertIn("checks", report)

        # API endpoint probe
        response = self.client.get("/api/data/quality")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "HEALTHY")
        self.assertEqual(data["passed_checks"], data["total_checks"])

    def test_cost_assumptions_and_endpoint(self) -> None:
        """Verify documented cost assumptions matrix is accessible via service and API."""
        assumptions = get_cost_assumptions()
        self.assertEqual(assumptions["currency"], "INR (₹)")
        self.assertIn("component_costs_inr", assumptions)
        self.assertIn("freight_rates_inr", assumptions)
        self.assertIn("contract_sla_penalty_rates_inr_per_day", assumptions)

        response = self.client.get("/api/data/assumptions")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["currency"], "INR (₹)")
        self.assertIn("alternate_vendor_premiums", data)

    def test_agent_roster_permissions_and_schemas(self) -> None:
        """Verify GET /api/agents/info returns inputs, outputs, permissions, and schemas."""
        response = self.client.get("/api/agents/info")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Check coordinator
        coord = data["coordinator"]
        self.assertIn("permissions", coord)
        self.assertIn("inputs", coord)
        self.assertIn("outputs", coord)
        self.assertIn("shared_data_schemas", coord)
        self.assertIn("EXECUTE_MULTI_AGENT_PIPELINE", coord["permissions"])

        # Check domain agents
        agents = data["agents"]
        self.assertEqual(len(agents), 4)
        for agent in agents:
            self.assertIn("inputs", agent, f"Missing inputs for {agent['name']}")
            self.assertIn("outputs", agent, f"Missing outputs for {agent['name']}")
            self.assertIn("permissions", agent, f"Missing permissions for {agent['name']}")
            self.assertIn("shared_data_schemas", agent, f"Missing shared schemas for {agent['name']}")

    def test_coordinator_conflict_resolutions_and_constraints(self) -> None:
        """Verify Coordinator returns explicit conflict resolutions and constraint validations."""
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

        self.assertIn("conflict_resolutions", data)
        self.assertGreaterEqual(len(data["conflict_resolutions"]), 4)
        for cr in data["conflict_resolutions"]:
            self.assertEqual(cr["status"], "RESOLVED_OPTIMAL")

        self.assertIn("constraint_validations", data)
        self.assertGreaterEqual(len(data["constraint_validations"]), 4)
        for cv in data["constraint_validations"]:
            self.assertTrue(cv["is_satisfied"])

        self.assertEqual(data["confidence_score"], 96.4)
        self.assertIn("governance_details", data)
        self.assertTrue(data["governance_details"]["dual_signoff_required"])

    def test_deliverable6_eight_evaluation_metrics(self) -> None:
        """Verify Google OR-Tools optimization computes all 8 required Deliverable 6 evaluation metrics."""
        opt_input = OptimizationInput(horizon_days=7, shutdown_duration_days=7)
        result: OptimizationResult = self.solver.solve(opt_input)

        # Verify all 8 metrics on optimized plan
        opt_plan = result.optimized_plan
        self.assertGreaterEqual(opt_plan.fill_rate, 90.0)             # 1. fill rate
        self.assertLessEqual(opt_plan.backorders, 250)                # 2. backorders
        self.assertGreater(opt_plan.total_landed_cost, 0.0)           # 3. total landed cost
        self.assertGreaterEqual(opt_plan.recovery_time_days, 1)       # 4. recovery time
        self.assertGreater(opt_plan.inventory_days, 0.0)              # 5. inventory days
        self.assertEqual(opt_plan.constraint_violations, 0)           # 6. constraint violations
        self.assertGreater(opt_plan.runtime_ms, 0.0)                  # 7. runtime
        self.assertIn("HIGH", opt_plan.recommendation_stability)      # 8. recommendation stability

        # Verify 8-metric evaluation scorecard dictionary
        scorecard = result.evaluation_metrics
        expected_metrics = [
            "fill_rate",
            "backorders",
            "total_landed_cost",
            "recovery_time",
            "inventory_days",
            "constraint_violations",
            "runtime",
            "recommendation_stability",
        ]
        for metric_key in expected_metrics:
            self.assertIn(metric_key, scorecard, f"Missing scorecard metric: {metric_key}")
            self.assertIn("baseline", scorecard[metric_key])
            self.assertIn("heuristic", scorecard[metric_key])
            self.assertIn("optimized", scorecard[metric_key])

        # Verify simulator API returns scorecard and confidence
        sim_res = self.client.post("/api/simulator/run", json={"duration": 7, "demand_change": 0})
        self.assertEqual(sim_res.status_code, 200)
        sim_data = sim_res.json()
        self.assertIn("evaluation_metrics", sim_data)
        self.assertIn("confidence_score", sim_data)
        self.assertEqual(sim_data["confidence_score"], 96.4)

    def test_governance_analysis_endpoint(self) -> None:
        """Verify GET /api/approvals/governance returns policy compliance and budget controls."""
        response = self.client.get("/api/approvals/governance")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["compliance_status"], "100% COMPLIANT")
        self.assertTrue(data["dual_signoff_required"])
        self.assertEqual(data["dual_signoff_threshold_inr"], 1000000.0)
        self.assertEqual(data["emergency_budget_cap_inr"], 5000000.0)
        self.assertIn("lead_planner", data)
