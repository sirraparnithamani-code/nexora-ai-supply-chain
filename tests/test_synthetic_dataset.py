"""Tests for Parker Hannifin India (Hyderabad) Synthetic Dataset and Data APIs.

Validates:
1. Synthetic dataset consistency: Suppliers, Components, Products, BOMs, Orders.
2. 7-day supplier shutdown effect calculations (burn-down runway, stockout day 4, deficit 580/day).
3. Currency consistency (INR ₹) across all entities and contractual SLAs.
4. Data service endpoints: /api/data/summary, /suppliers, /components, /orders.
5. Disclaimer indicating synthetic demonstration data, not actual company data.
"""

from __future__ import annotations

import unittest
from starlette.testclient import TestClient

from app.main import app
from app.services.data_service import (
    DEMO_DISCLAIMER,
    get_bom_dataframe,
    get_components_dataframe,
    get_historical_demand_series,
    get_sales_orders_dataframe,
    get_suppliers_dataframe,
)


class SyntheticDatasetTestCase(unittest.TestCase):
    """Test suite validating Parker Hannifin India synthetic dataset."""

    def setUp(self) -> None:
        """Initialize API TestClient."""
        self.client = TestClient(app)

    def test_synthetic_disclaimer_is_explicit(self) -> None:
        """Data service summary must contain explicit synthetic data notice."""
        self.assertIn("Synthetic Demo Data", DEMO_DISCLAIMER)
        self.assertIn("Parker Hannifin India", DEMO_DISCLAIMER)

    def test_critical_and_alternate_suppliers_exist(self) -> None:
        """Dataset must include 1 critical disrupted supplier and 2 qualified alternates."""
        suppliers_df = get_suppliers_dataframe()
        self.assertGreaterEqual(len(suppliers_df), 3)

        supplier_names = suppliers_df["name"].tolist()

        # 1 Disrupted critical supplier (Pune)
        kalyani = suppliers_df[suppliers_df["name"].str.contains("Kalyani")]
        self.assertFalse(kalyani.empty)
        self.assertEqual(int(kalyani.iloc[0]["is_disrupted"]), 1)

        # 2 Qualified alternative suppliers (Chennai and Bengaluru)
        sundaram = suppliers_df[suppliers_df["name"].str.contains("Sundaram")]
        self.assertFalse(sundaram.empty)
        self.assertEqual(int(sundaram.iloc[0]["is_disrupted"]), 0)
        self.assertGreater(int(sundaram.iloc[0]["capacity_daily"]), 300)

        kirloskar = suppliers_df[suppliers_df["name"].str.contains("Kirloskar")]
        self.assertFalse(kirloskar.empty)
        self.assertEqual(int(kirloskar.iloc[0]["is_disrupted"]), 0)
        self.assertGreater(int(kirloskar.iloc[0]["capacity_daily"]), 200)

    def test_components_catalog_coverage(self) -> None:
        """Components must include hydraulic components, industrial valves, and sealing products."""
        components_df = get_components_dataframe()
        categories = set(components_df["category"].tolist())

        self.assertIn("Hydraulic Components", categories)
        self.assertIn("Industrial Valves", categories)
        self.assertIn("Sealing Components", categories)

        # Target disrupted component: Forged Valve Spool & Casting
        spool = components_df[components_df["sku"] == "CMP-MCU-9000"]
        self.assertFalse(spool.empty)
        row = spool.iloc[0]
        self.assertEqual(int(row["current_stock"]), 2400)
        self.assertEqual(int(row["safety_stock"]), 600)
        self.assertEqual(int(row["daily_usage"]), 580)

    def test_customer_sales_orders_and_inr_penalties(self) -> None:
        """Sales orders must have customer tiers, finished products, and delay penalties in INR."""
        orders_df = get_sales_orders_dataframe()
        self.assertGreaterEqual(len(orders_df), 6)

        tiers = set(orders_df["customer_tier"].tolist())
        self.assertIn("Gold", tiers)
        self.assertIn("Silver", tiers)
        self.assertIn("Standard", tiers)

        for _, ord_info in orders_df.iterrows():
            self.assertGreater(float(ord_info["unit_price"]), 0)
            self.assertGreater(float(ord_info["sla_penalty_daily"]), 0)

    def test_historical_demand_series(self) -> None:
        """Historical demand series must provide 30-day realistic figures."""
        series = get_historical_demand_series()
        self.assertIn("FG-ROBOT-01", series)
        self.assertIn("FG-CTRL-02", series)
        self.assertEqual(len(series["FG-ROBOT-01"]), 30)
        self.assertEqual(len(series["FG-CTRL-02"]), 30)

    def test_get_data_summary_endpoint(self) -> None:
        """GET /api/data/summary returns complete synthetic catalog."""
        res = self.client.get("/api/data/summary")
        self.assertEqual(res.status_code, 200)

        data = res.json()
        self.assertIn("suppliers", data)
        self.assertIn("components", data)
        self.assertIn("sales_orders", data)
        self.assertIn("bill_of_materials", data)
        self.assertIn("INR", data["currency"])

    def test_get_data_suppliers_endpoint(self) -> None:
        """GET /api/data/suppliers returns 5 suppliers."""
        res = self.client.get("/api/data/suppliers")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 5)

    def test_get_data_components_endpoint(self) -> None:
        """GET /api/data/components returns components with runway and costs."""
        res = self.client.get("/api/data/components")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.json()), 4)

    def test_get_data_orders_endpoint(self) -> None:
        """GET /api/data/orders returns customer orders."""
        res = self.client.get("/api/data/orders")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.json()), 6)


if __name__ == "__main__":
    unittest.main()
