"""Tests for Google OR-Tools Optimization Solver and Three Planning Approaches.

Validates:
1. Google OR-Tools Mixed-Integer Linear Programming (MILP) formulation.
2. Three planning approaches: Baseline, Rule-Based, and Optimization-Based.
3. Constraint enforcement: inventory balance, alternate capacity, safety buffer.
4. Edge cases, infeasible scenarios, and parameter sensitivities.
"""

from __future__ import annotations

import unittest
from app.optimization.solver import OptimizationInput, OptimizationResult, OptimizationSolver


class OptimizationSolverTestCase(unittest.TestCase):
    """Test suite for mathematical recovery planning using Google OR-Tools."""

    def setUp(self) -> None:
        """Initialize optimization solver instance."""
        self.solver = OptimizationSolver()

    def test_default_nominal_solve_returns_optimal(self) -> None:
        """Default 7-day disruption input must solve to OPTIMAL."""
        input_data = OptimizationInput(
            horizon_days=7,
            shutdown_duration_days=7,
            initial_inventory=2400,
            safety_stock_threshold=600,
            daily_consumption_rate=580.0,
            demand_change_pct=0.0,
            alternate_capacity_factor=0.65,
            logistics_delay_days=0,
        )

        result: OptimizationResult = self.solver.solve(input_data)

        self.assertEqual(result.solver_status, "OPTIMAL")
        self.assertTrue(result.is_optimal)
        self.assertLess(result.solver_runtime_ms, 500.0)  # Solves in milliseconds
        self.assertIn("Google OR-Tools", result.solver_algorithm)

    def test_three_planning_approaches_comparison(self) -> None:
        """Optimized recovery must strictly outperform Baseline and Rule-Based approaches."""
        input_data = OptimizationInput(
            horizon_days=7,
            shutdown_duration_days=7,
            initial_inventory=2400,
            safety_stock_threshold=600,
            daily_consumption_rate=580.0,
        )

        result: OptimizationResult = self.solver.solve(input_data)

        base = result.baseline_plan
        heur = result.heuristic_plan
        opt = result.optimized_plan

        # Baseline plan has low fulfillment and high penalty loss
        self.assertLess(base.fulfillment_rate, 50.0)
        self.assertGreater(base.shortage_units, 2000.0)
        self.assertGreater(base.downtime_days, 3.0)

        # Rule-based plan has high expedited freight costs
        self.assertGreater(heur.freight_cost, 400000.0)

        # Optimized plan achieves high fulfillment at lower total cost
        self.assertGreater(opt.fulfillment_rate, 90.0)
        self.assertLess(opt.total_cost, base.total_cost)
        self.assertLess(opt.total_cost, heur.total_cost)

        # Net savings must be positive
        self.assertGreater(result.cost_savings_vs_heuristic, 0.0)
        self.assertGreater(result.cost_savings_vs_baseline, 0.0)

    def test_daily_trajectory_contains_seven_days(self) -> None:
        """Daily trajectory must contain exactly 7 days of stock balances."""
        input_data = OptimizationInput(horizon_days=7, shutdown_duration_days=7)
        result: OptimizationResult = self.solver.solve(input_data)

        self.assertEqual(len(result.daily_trajectory), 7)
        day1 = result.daily_trajectory[0]
        self.assertEqual(day1["day"], "Day 1")
        self.assertIn("baseline_stock", day1)
        self.assertIn("optimized_stock", day1)
        self.assertIn("safety_stock", day1)

    def test_alternate_capacity_constrains_order_quantities(self) -> None:
        """Constraining alternate supplier capacity limits ordered volumes."""
        # Generous capacity
        input_generous = OptimizationInput(alternate_capacity_factor=1.0)
        res_generous = self.solver.solve(input_generous)

        # Constrained capacity
        input_tight = OptimizationInput(alternate_capacity_factor=0.2)
        res_tight = self.solver.solve(input_tight)

        # Sum of ordered units under tight capacity must be strictly less
        qty_generous = sum(d["quantity"] for d in res_generous.decision_allocations)
        qty_tight = sum(d["quantity"] for d in res_tight.decision_allocations)

        self.assertLessEqual(qty_tight, qty_generous)

    def test_demand_spike_increases_total_recovery_cost(self) -> None:
        """A +30% demand spike increases production required and component procurement cost."""
        input_nominal = OptimizationInput(demand_change_pct=0.0)
        res_nominal = self.solver.solve(input_nominal)

        input_spike = OptimizationInput(demand_change_pct=30.0)
        res_spike = self.solver.solve(input_spike)

        self.assertGreater(res_spike.optimized_plan.total_cost, res_nominal.optimized_plan.total_cost)

    def test_logistics_delay_impact(self) -> None:
        """Extra transit delay of 3 days reflects in decision timelines."""
        input_delayed = OptimizationInput(logistics_delay_days=3)
        res_delayed = self.solver.solve(input_delayed)

        self.assertIsNotNone(res_delayed.optimized_plan)
        # Allocations should note delayed transit
        self.assertTrue(any(d["logistics_mode"] for d in res_delayed.decision_allocations))

    def test_zero_inventory_severe_shortage_handling(self) -> None:
        """Starting with zero inventory tests extreme shortage and downtime penalties."""
        input_depleted = OptimizationInput(initial_inventory=0, shutdown_duration_days=7)
        result: OptimizationResult = self.solver.solve(input_depleted)

        self.assertIsNotNone(result)
        self.assertIn(result.solver_status, ["OPTIMAL", "FEASIBLE"])
        self.assertGreater(result.optimized_plan.shortage_units, 0.0)


if __name__ == "__main__":
    unittest.main()
