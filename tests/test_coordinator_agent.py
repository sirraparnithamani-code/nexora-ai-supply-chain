"""Unit tests for Coordinator Agent."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.agents.coordinator_agent import CoordinatorAgent
from app.database import init_db
from app.schemas.agents import CoordinatorAssessmentRequest


class CoordinatorAgentTestCase(unittest.TestCase):
    """Test suite for Coordinator Agent multi-agent orchestration and synthesis."""

    @classmethod
    def setUpClass(cls) -> None:
        init_db()
        cls.agent = CoordinatorAgent()

    def test_full_coordinated_pipeline_execution(self) -> None:
        """Verify sequential execution of all four domain agents and structured synthesis."""
        req = CoordinatorAssessmentRequest(
            shutdown_duration_days=7,
            demand_change_pct=0.0,
            disrupted_supplier_id="SUP-001",
            target_sku="CMP-MCU-9000",
            alternate_capacity_factor=1.0,
        )
        res = self.agent.run(req)

        # 1. Pipeline verification
        self.assertEqual(len(res.execution_pipeline), 5)
        self.assertIn("Demand Agent", res.execution_pipeline[0])
        self.assertIn("Inventory Agent", res.execution_pipeline[1])
        self.assertIn("Supplier-Risk Agent", res.execution_pipeline[2])
        self.assertIn("Logistics Agent", res.execution_pipeline[3])
        self.assertIn("Coordinator Agent", res.execution_pipeline[4])

        # 2. Sub-agent payload integration
        self.assertIsNotNone(res.demand_assessment)
        self.assertIsNotNone(res.inventory_assessment)
        self.assertIsNotNone(res.supplier_risk_assessment)
        self.assertIsNotNone(res.logistics_assessment)

        # 3. Shortages identified structure
        shortages = res.shortages_identified
        self.assertEqual(shortages["critical_component"], "CMP-MCU-9000")
        self.assertGreater(shortages["current_on_hand"], 0)
        self.assertGreater(shortages["safety_stock_threshold"], 0)
        self.assertIsNotNone(shortages["stockout_day"])
        self.assertGreater(shortages["net_7day_deficit_units"], 0)
        self.assertGreater(shortages["production_requirements_units"], 0)
        self.assertTrue(len(shortages["assembly_lines_at_risk"]) > 0)

        # 4. Risks and impacts structure
        risks = res.risks_and_impacts
        self.assertTrue(risks["single_source_failure"])
        self.assertGreater(risks["revenue_at_risk"], 0.0)
        self.assertGreater(risks["daily_sla_penalty_exposure"], 0.0)
        self.assertIn("production_line_a_impact", risks)

        # 5. Recovery options and action items
        self.assertGreaterEqual(len(res.recovery_options), 3)
        total_costs = sum(item.estimated_cost for item in res.recovery_options)
        self.assertEqual(res.estimated_total_mitigation_cost, total_costs)

        # 6. Governance & human approval
        self.assertTrue(res.requires_human_approval)
        self.assertEqual(res.approval_status, "PENDING_APPROVAL")
        self.assertGreaterEqual(len(res.actionable_recommendations), 4)

        # 7. Model methodology transparency
        self.assertIn("Non-ML", res.model_type)
        self.assertIn("OR-Tools", res.methodology)

    def test_alternate_capacity_factor_slider(self) -> None:
        """Verify reduced alternate capacity factor throttles capacity and impacts fulfillment."""
        normal_req = CoordinatorAssessmentRequest(alternate_capacity_factor=1.0)
        normal_res = self.agent.run(normal_req)

        restricted_req = CoordinatorAssessmentRequest(alternate_capacity_factor=0.3)
        restricted_res = self.agent.run(restricted_req)

        self.assertLess(
            restricted_res.supplier_risk_assessment.total_alternate_daily_capacity,
            normal_res.supplier_risk_assessment.total_alternate_daily_capacity,
        )
        self.assertFalse(restricted_res.supplier_risk_assessment.can_cover_daily_deficit)
        self.assertLess(restricted_res.projected_fulfillment_rate, normal_res.projected_fulfillment_rate)

    def test_demand_spike_scenario_coordination(self) -> None:
        """Verify coordinator adapts when demand changes by +30%."""
        req = CoordinatorAssessmentRequest(demand_change_pct=30.0)
        res = self.agent.run(req)

        self.assertEqual(res.demand_assessment.demand_change_pct, 30.0)
        self.assertGreater(res.demand_assessment.total_revenue_at_risk, 0.0)


if __name__ == "__main__":
    unittest.main()
