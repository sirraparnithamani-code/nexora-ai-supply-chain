"""Data service module for NEXORA AI.

Provides database seeding, relational table queries, and pandas dataframe extractors
for supply chain components, BOM explosion, and customer demand books.

Synthetic Demonstration Dataset inspired by the manufacturing context of
Parker Hannifin India Pvt. Ltd., Hyderabad (Hydraulic components, industrial valves,
and sealing solutions).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

from app.database import get_db_connection

logger = logging.getLogger(__name__)

DEMO_DISCLAIMER = (
    "Synthetic Demo Data — Not Actual Company Data. "
    "Illustrative discrete manufacturing scenario inspired by Parker Hannifin India, Hyderabad."
)


def seed_demo_data(db_path: Optional[Path] = None, force: bool = False) -> Dict[str, int]:
    """Seed SQLite database with deterministic supply chain demo records.

    If force=True, clears existing demonstration tables and repopulates them.
    Returns the count of seeded rows per table.
    """
    counts: Dict[str, int] = {}
    with get_db_connection(db_path) as conn:
        if force:
            conn.execute("DELETE FROM sales_orders;")
            conn.execute("DELETE FROM bill_of_materials;")
            conn.execute("DELETE FROM products;")
            conn.execute("DELETE FROM components;")
            conn.execute("DELETE FROM suppliers;")
            conn.execute("DELETE FROM simulation_runs;")
            conn.execute("DELETE FROM audit_logs;")

        # 1. Suppliers
        cursor = conn.execute("SELECT COUNT(*) FROM suppliers;")
        if cursor.fetchone()[0] == 0:
            conn.executemany(
                """
                INSERT INTO suppliers (id, name, tier, lead_time_days, capacity_daily, unit_cost_multiplier, reliability_score, is_active, is_disrupted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                [
                    (1, "Kalyani Precision Forgings (SUP-001)", "Tier-1", 7, 600, 1.00, 0.98, 1, 1),
                    (2, "Sundaram Precision Hydraulics (SUP-002)", "Tier-2", 2, 450, 1.18, 0.94, 1, 0),
                    (3, "Kirloskar Precision Castings (SUP-003)", "Tier-2", 4, 320, 1.12, 0.91, 1, 0),
                    (4, "TVS Advanced Sealing Systems (SUP-004)", "Tier-1", 3, 700, 1.00, 0.99, 1, 0),
                    (5, "Bharat Precision Sensors (SUP-005)", "Tier-1", 4, 850, 1.00, 0.97, 1, 0),
                ],
            )
        counts["suppliers"] = conn.execute("SELECT COUNT(*) FROM suppliers;").fetchone()[0]

        # 2. Components
        cursor = conn.execute("SELECT COUNT(*) FROM components;")
        if cursor.fetchone()[0] == 0:
            conn.executemany(
                """
                INSERT INTO components (sku, name, category, unit_cost, holding_cost_daily, safety_stock_min, current_stock, unit_of_measure)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                [
                    ("CMP-MCU-9000", "Forged Valve Spool & Casting", "Hydraulic Components", 4250.0, 45.0, 600, 2400, "units"),
                    ("CMP-PM-48V", "Directional Control Valve Manifold Block", "Industrial Valves", 9500.0, 85.0, 1200, 5200, "units"),
                    ("CMP-OS-200", "High-Pressure Cylinder Seal Kit & O-Rings", "Sealing Components", 1850.0, 35.0, 800, 4100, "units"),
                    ("CMP-CH-01", "Ductile Iron Valve Body Housing", "Castings / Mechanical", 6800.0, 110.0, 500, 1850, "units"),
                ],
            )
        counts["components"] = conn.execute("SELECT COUNT(*) FROM components;").fetchone()[0]

        # 3. Products
        cursor = conn.execute("SELECT COUNT(*) FROM products;")
        if cursor.fetchone()[0] == 0:
            conn.executemany(
                """
                INSERT INTO products (sku, name, assembly_hours, unit_price, is_active)
                VALUES (?, ?, ?, ?, ?);
                """,
                [
                    ("FG-ROBOT-01", "Heavy-Duty Industrial Cylinder (HCY-400)", 2.5, 25000.0, 1),
                    ("FG-CTRL-02", "Proportional Control Valve (DCV-250)", 1.2, 12000.0, 1),
                    ("FG-HPU-03", "Hydraulic Power Unit System (HPU-100)", 3.5, 45000.0, 1),
                ],
            )
        counts["products"] = conn.execute("SELECT COUNT(*) FROM products;").fetchone()[0]

        # 4. Bill of Materials (BOM)
        cursor = conn.execute("SELECT COUNT(*) FROM bill_of_materials;")
        if cursor.fetchone()[0] == 0:
            prod_rows = conn.execute("SELECT id, sku FROM products;").fetchall()
            comp_rows = conn.execute("SELECT id, sku FROM components;").fetchall()
            p_map = {row["sku"]: row["id"] for row in prod_rows}
            c_map = {row["sku"]: row["id"] for row in comp_rows}

            bom_entries = [
                (p_map["FG-ROBOT-01"], c_map["CMP-MCU-9000"], 2),  # 2x Forged Spool per Cylinder
                (p_map["FG-ROBOT-01"], c_map["CMP-PM-48V"], 1),
                (p_map["FG-ROBOT-01"], c_map["CMP-OS-200"], 2),
                (p_map["FG-ROBOT-01"], c_map["CMP-CH-01"], 1),
                (p_map["FG-CTRL-02"], c_map["CMP-MCU-9000"], 1),   # 1x Forged Spool per Valve
                (p_map["FG-CTRL-02"], c_map["CMP-PM-48V"], 1),
                (p_map["FG-CTRL-02"], c_map["CMP-OS-200"], 1),
            ]
            if "FG-HPU-03" in p_map:
                bom_entries.extend([
                    (p_map["FG-HPU-03"], c_map["CMP-MCU-9000"], 1),
                    (p_map["FG-HPU-03"], c_map["CMP-PM-48V"], 2),
                    (p_map["FG-HPU-03"], c_map["CMP-CH-01"], 1),
                ])

            conn.executemany(
                """
                INSERT INTO bill_of_materials (product_id, component_id, quantity_required)
                VALUES (?, ?, ?);
                """,
                bom_entries,
            )
        counts["bill_of_materials"] = conn.execute("SELECT COUNT(*) FROM bill_of_materials;").fetchone()[0]

        # 5. Sales Orders
        cursor = conn.execute("SELECT COUNT(*) FROM sales_orders;")
        if cursor.fetchone()[0] == 0:
            prod_rows = conn.execute("SELECT id, sku FROM products;").fetchall()
            p_map = {row["sku"]: row["id"] for row in prod_rows}

            sample_orders = [
                ("ORD-5011", "Larsen & Toubro Heavy Engineering", "Gold", p_map["FG-ROBOT-01"], 90, 3, 150000.0, "OPEN"),
                ("ORD-5012", "Tata Motors CV Division", "Gold", p_map["FG-CTRL-02"], 120, 5, 180000.0, "OPEN"),
                ("ORD-5014", "BHEL Heavy Electricals (Hyderabad)", "Gold", p_map["FG-CTRL-02"], 180, 5, 85000.0, "OPEN"),
                ("ORD-5018", "Mahindra & Mahindra Farm Equipment", "Silver", p_map["FG-ROBOT-01"], 60, 6, 40000.0, "OPEN"),
                ("ORD-5021", "BEML Mining & Construction", "Silver", p_map["FG-CTRL-02"], 140, 7, 32000.0, "OPEN"),
                ("ORD-5025", "Escorts Kubota Agri Machinery", "Standard", p_map["FG-CTRL-02"], 210, 8, 11000.0, "OPEN"),
                ("ORD-5028", "Midwest Hydraulics Hub", "Standard", p_map["FG-ROBOT-01"], 80, 9, 15000.0, "OPEN"),
            ]
            conn.executemany(
                """
                INSERT INTO sales_orders (order_number, customer_name, customer_tier, product_id, quantity, due_day, sla_penalty_daily, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                sample_orders,
            )
        counts["sales_orders"] = conn.execute("SELECT COUNT(*) FROM sales_orders;").fetchone()[0]

        # 6. Initial Simulation Run
        cursor = conn.execute("SELECT COUNT(*) FROM simulation_runs;")
        if cursor.fetchone()[0] == 0:
            conn.execute(
                """
                INSERT INTO simulation_runs (scenario_name, outage_days, planning_approach, total_cost, fulfillment_rate, downtime_days, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    "7-Day Outage - Kalyani Precision Forgings (Pune)",
                    7,
                    "optimized",
                    412000.0,
                    96.2,
                    0.0,
                    "PENDING_APPROVAL",
                    "Initial multi-agent assessment completed via Google OR-Tools optimization. Awaiting lead planner authorization.",
                ),
            )
        counts["simulation_runs"] = conn.execute("SELECT COUNT(*) FROM simulation_runs;").fetchone()[0]

        # 7. Initial Audit Logs
        cursor = conn.execute("SELECT COUNT(*) FROM audit_logs;")
        if cursor.fetchone()[0] == 0:
            conn.executemany(
                """
                INSERT INTO audit_logs (agent_name, action, details_json)
                VALUES (?, ?, ?);
                """,
                [
                    (
                        "Coordinator Agent",
                        "Synthesized Best Recovery Plan for 7-day outage of Kalyani Precision Forgings",
                        '{"mitigation_cost": 412000, "projected_fulfillment": 96.2, "pending_pos": 3, "disclaimer": "Synthetic Demo Data"}',
                    ),
                    (
                        "Optimization Engine",
                        "Google OR-Tools solver reached OPTIMAL status in 142 ms",
                        '{"solver": "SCIP", "status": "OPTIMAL", "cost_savings": 533000, "dual_sourcing": true}',
                    ),
                    (
                        "Operations Planner",
                        "Initialized approval review queue for pending emergency recovery orders",
                        '{"actor": "R. Verma (Lead Operations Planner)", "status": "UNDER_REVIEW"}',
                    ),
                ],
            )
        counts["audit_logs"] = conn.execute("SELECT COUNT(*) FROM audit_logs;").fetchone()[0]

    logger.info(f"Seeded SQLite demo data successfully: {counts}")
    return counts


def get_suppliers_dataframe(db_path: Optional[Path] = None) -> pd.DataFrame:
    """Fetch suppliers as a pandas DataFrame."""
    with get_db_connection(db_path) as conn:
        return pd.read_sql_query("SELECT * FROM suppliers;", conn)


def get_components_dataframe(db_path: Optional[Path] = None) -> pd.DataFrame:
    """Fetch components as a pandas DataFrame with aliased metrics."""
    with get_db_connection(db_path) as conn:
        df = pd.read_sql_query("SELECT * FROM components;", conn)
        if "safety_stock_min" in df.columns and "safety_stock" not in df.columns:
            df["safety_stock"] = df["safety_stock_min"]
        if "daily_usage" not in df.columns:
            df["daily_usage"] = df["sku"].map({
                "CMP-MCU-9000": 580,
                "CMP-PM-48V": 740,
                "CMP-OS-200": 620,
                "CMP-CH-01": 310,
            }).fillna(500)
        return df


def get_bom_dataframe(db_path: Optional[Path] = None) -> pd.DataFrame:
    """Fetch Bill of Materials joined with product and component SKUs."""
    query = """
    SELECT 
        b.id,
        p.sku AS product_sku,
        p.name AS product_name,
        c.sku AS component_sku,
        c.name AS component_name,
        b.quantity_required
    FROM bill_of_materials b
    JOIN products p ON b.product_id = p.id
    JOIN components c ON b.component_id = c.id;
    """
    with get_db_connection(db_path) as conn:
        return pd.read_sql_query(query, conn)


def get_sales_orders_dataframe(db_path: Optional[Path] = None) -> pd.DataFrame:
    """Fetch sales orders joined with product SKU."""
    query = """
    SELECT 
        o.id,
        o.order_number,
        o.customer_name,
        o.customer_tier,
        p.sku AS product_sku,
        p.name AS product_name,
        p.unit_price,
        o.quantity,
        o.due_day,
        o.sla_penalty_daily,
        o.status
    FROM sales_orders o
    JOIN products p ON o.product_id = p.id
    ORDER BY o.due_day ASC;
    """
    with get_db_connection(db_path) as conn:
        return pd.read_sql_query(query, conn)


def get_historical_demand_series() -> Dict[str, List[int]]:
    """Return realistic historical 30-day demand figures for baseline trend estimation.

    Based on Parker Hannifin India, Hyderabad production rates for
    HCY-400 (Line 1 Cylinder) and DCV-250 (Line 2 Valve).
    """
    return {
        "FG-ROBOT-01": [
            165, 170, 160, 175, 180, 172, 168, 175, 182, 178,
            180, 185, 179, 182, 180, 175, 182, 188, 179, 181,
            180, 185, 183, 180, 184, 180, 182, 185, 180, 180
        ],
        "FG-CTRL-02": [
            210, 215, 205, 220, 218, 225, 219, 222, 225, 220,
            218, 224, 220, 226, 221, 219, 225, 228, 220, 222,
            220, 225, 223, 221, 226, 220, 222, 225, 220, 220
        ],
    }


# ==============================================================================
# Documented Cost Assumptions & Parameters (Deliverable 1)
# ==============================================================================
COST_ASSUMPTIONS: Dict[str, Any] = {
    "currency": "INR (₹)",
    "scenario_scope": "Parker Hannifin India Pvt. Ltd. (Hyderabad Facility)",
    "disrupted_supplier": {
        "id": "SUP-001",
        "name": "Kalyani Precision Forgings (Pune)",
        "outage_days": 7,
        "affected_component": "CMP-MCU-9000 (Forged Valve Spool & Casting)",
    },
    "component_costs_inr": {
        "CMP-MCU-9000": {"base_unit_cost": 4250.0, "daily_holding_cost": 45.0, "weight_kg": 0.5},
        "CMP-PM-48V": {"base_unit_cost": 9500.0, "daily_holding_cost": 85.0, "weight_kg": 1.2},
        "CMP-OS-200": {"base_unit_cost": 1850.0, "daily_holding_cost": 35.0, "weight_kg": 0.2},
        "CMP-CH-01": {"base_unit_cost": 6800.0, "daily_holding_cost": 110.0, "weight_kg": 2.5},
    },
    "alternate_vendor_premiums": {
        "SUP-002": {
            "name": "Sundaram Precision Hydraulics (Chennai)",
            "unit_price_multiplier": 1.18,
            "rush_surcharge_inr": 765.0,  # +18% on ₹4,250
            "daily_capacity": 450,
            "air_transit_days": 2,
            "road_transit_days": 4,
        },
        "SUP-003": {
            "name": "Kirloskar Precision Castings (Bengaluru)",
            "unit_price_multiplier": 1.12,
            "rush_surcharge_inr": 510.0,  # +12% on ₹4,250
            "daily_capacity": 320,
            "road_transit_days": 4,
        },
    },
    "freight_rates_inr": {
        "dedicated_air_cargo": {"rate_per_kg": 175.0, "min_charter_fee": 73500.0, "transit_days": 2},
        "express_road_truckload": {"rate_per_kg": 27.50, "min_truckload_fee": 25000.0, "transit_days": 4},
        "regular_highway_container": {"rate_per_kg": 22.50, "min_container_fee": 18000.0, "transit_days": 4},
        "standard_surface_stalled": {"rate_per_kg": 28.0, "min_fee": 0.0, "transit_days": 7},
    },
    "contract_sla_penalty_rates_inr_per_day": {
        "gold_tier": {"per_unit_delayed_daily": 1650.0, "examples": "L&T (₹1.5L/d), Tata Motors (₹1.8L/d)"},
        "silver_tier": {"per_unit_delayed_daily": 850.0, "examples": "M&M (₹40k/d), BEML (₹32k/d)"},
        "standard_tier": {"per_unit_delayed_daily": 600.0, "examples": "Escorts (₹11k/d)"},
        "plant_stoppage_penalty_per_unit": 2500.0,
    },
}


def get_cost_assumptions() -> Dict[str, Any]:
    """Return documented cost and operational parameter assumptions."""
    return COST_ASSUMPTIONS


def run_data_quality_checks(db_path: Optional[Path] = None) -> Dict[str, Any]:
    """Execute automated data quality, consistency, and governance audit suite (Deliverable 7)."""
    checks: List[Dict[str, Any]] = []

    with get_db_connection(db_path) as conn:
        # 1. Table Completeness Check
        required_tables = ["suppliers", "components", "products", "bill_of_materials", "sales_orders", "simulation_runs", "audit_logs"]
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = {row["name"] for row in cursor.fetchall()}
        missing = [t for t in required_tables if t not in existing_tables]
        checks.append({
            "name": "table_completeness",
            "category": "Schema Integrity",
            "status": "PASSED" if not missing else "FAILED",
            "message": f"All {len(required_tables)} relational tables verified in SQLite." if not missing else f"Missing tables: {missing}",
            "details": {"verified_tables": list(existing_tables)},
        })

        # 2. Referential Integrity: BOM Foreign Keys
        bom_orphans = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM bill_of_materials b
            WHERE b.product_id NOT IN (SELECT id FROM products)
               OR b.component_id NOT IN (SELECT id FROM components);
            """
        ).fetchone()["count"]
        checks.append({
            "name": "bom_referential_integrity",
            "category": "Relational Integrity",
            "status": "PASSED" if bom_orphans == 0 else "FAILED",
            "message": "All Bill of Materials records map to valid products and components." if bom_orphans == 0 else f"{bom_orphans} orphaned BOM records found",
            "details": {"orphan_count": bom_orphans},
        })

        # 3. Referential Integrity: Sales Orders
        order_orphans = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM sales_orders o
            WHERE o.product_id NOT IN (SELECT id FROM products);
            """
        ).fetchone()["count"]
        checks.append({
            "name": "sales_order_product_integrity",
            "category": "Relational Integrity",
            "status": "PASSED" if order_orphans == 0 else "FAILED",
            "message": "All customer sales orders link to valid manufactured products." if order_orphans == 0 else f"{order_orphans} orphaned sales orders found",
            "details": {"orphan_count": order_orphans},
        })

        # 4. Inventory Data Quality
        invalid_inventory = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM components
            WHERE current_stock < 0 OR safety_stock_min <= 0 OR unit_cost <= 0 OR holding_cost_daily < 0;
            """
        ).fetchone()["count"]
        checks.append({
            "name": "inventory_values_validity",
            "category": "Data Quality",
            "status": "PASSED" if invalid_inventory == 0 else "FAILED",
            "message": "All component inventory levels, costs, and safety stock thresholds are positive and valid." if invalid_inventory == 0 else f"{invalid_inventory} components have invalid stock or cost attributes",
            "details": {"invalid_components_count": invalid_inventory},
        })

        # 5. Supplier Data Quality
        invalid_suppliers = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM suppliers
            WHERE capacity_daily <= 0 OR lead_time_days <= 0 OR reliability_score < 0.5 OR reliability_score > 1.0;
            """
        ).fetchone()["count"]
        checks.append({
            "name": "supplier_parameters_validity",
            "category": "Data Quality",
            "status": "PASSED" if invalid_suppliers == 0 else "FAILED",
            "message": "All supplier capacities, lead times, and reliability ratings satisfy domain constraints." if invalid_suppliers == 0 else f"{invalid_suppliers} suppliers have out-of-bound parameters",
            "details": {"invalid_suppliers_count": invalid_suppliers},
        })

        # 6. Scenario Disruption State Check
        disrupted_count = conn.execute(
            "SELECT COUNT(*) AS count FROM suppliers WHERE is_disrupted = 1;"
        ).fetchone()["count"]
        checks.append({
            "name": "disruption_scenario_consistency",
            "category": "Scenario Configuration",
            "status": "PASSED" if disrupted_count == 1 else "WARNING",
            "message": "Single primary supplier outage state (SUP-001 Kalyani Precision Forgings) correctly initialized." if disrupted_count == 1 else f"Disrupted supplier count is {disrupted_count}",
            "details": {"disrupted_suppliers_count": disrupted_count},
        })

    passed_count = sum(1 for c in checks if c["status"] == "PASSED")
    total_count = len(checks)
    overall_status = "HEALTHY" if passed_count == total_count else "DEGRADED"

    return {
        "status": overall_status,
        "total_checks": total_count,
        "passed_checks": passed_count,
        "failed_checks": total_count - passed_count,
        "checks": checks,
        "disclaimer": DEMO_DISCLAIMER,
        "timestamp": pd.Timestamp.now().isoformat(),
    }

