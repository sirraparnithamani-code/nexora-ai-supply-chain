"""Database management module.

Handles SQLite connection pooling, WAL configuration, relational schema initialization,
and database health inspection.
"""

from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List

from app.config import get_settings

logger = logging.getLogger(__name__)

# Complete DDL script for supply chain resilience entities
SCHEMA_SQL = """
-- 1. Suppliers Table
CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    tier TEXT NOT NULL,                     -- e.g. 'Tier-1', 'Tier-2'
    lead_time_days INTEGER NOT NULL,
    capacity_daily INTEGER NOT NULL,
    unit_cost_multiplier REAL NOT NULL DEFAULT 1.0,
    reliability_score REAL NOT NULL DEFAULT 0.95,
    is_active INTEGER NOT NULL DEFAULT 1,
    is_disrupted INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Components / Raw Materials Table
CREATE TABLE IF NOT EXISTS components (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit_cost REAL NOT NULL,
    holding_cost_daily REAL NOT NULL,
    safety_stock_min INTEGER NOT NULL,
    current_stock INTEGER NOT NULL,
    unit_of_measure TEXT NOT NULL DEFAULT 'units',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Products / Finished Goods Table
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    assembly_hours REAL NOT NULL DEFAULT 1.0,
    unit_price REAL NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Bill of Materials (BOM) Table
CREATE TABLE IF NOT EXISTS bill_of_materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    component_id INTEGER NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    quantity_required INTEGER NOT NULL,
    UNIQUE(product_id, component_id)
);

-- 5. Sales Orders Table
CREATE TABLE IF NOT EXISTS sales_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT NOT NULL UNIQUE,
    customer_name TEXT NOT NULL,
    customer_tier TEXT NOT NULL,             -- 'Gold', 'Silver', 'Standard'
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL,
    due_day INTEGER NOT NULL,
    sla_penalty_daily REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'OPEN',     -- 'OPEN', 'FULFILLED', 'BACKLOGGED'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Simulation Runs & Scenarios Table
CREATE TABLE IF NOT EXISTS simulation_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_name TEXT NOT NULL,
    outage_days INTEGER NOT NULL DEFAULT 7,
    planning_approach TEXT NOT NULL,         -- 'baseline', 'heuristic', 'optimized'
    total_cost REAL,
    fulfillment_rate REAL,
    downtime_days REAL,
    status TEXT NOT NULL DEFAULT 'PENDING_APPROVAL', -- 'PENDING_APPROVAL', 'APPROVED', 'REJECTED'
    approved_by TEXT,
    approved_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Audit & Agent Decision Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    agent_name TEXT NOT NULL,
    action TEXT NOT NULL,
    details_json TEXT
);

-- Indices for performance
CREATE INDEX IF NOT EXISTS idx_suppliers_disrupted ON suppliers(is_disrupted);
CREATE INDEX IF NOT EXISTS idx_sales_orders_status ON sales_orders(status);
CREATE INDEX IF NOT EXISTS idx_bom_product ON bill_of_materials(product_id);
CREATE INDEX IF NOT EXISTS idx_sim_status ON simulation_runs(status);
"""


def get_db_path() -> Path:
    """Return the resolved database path from configuration."""
    return get_settings().database_path


@contextmanager
def get_db_connection(db_path: Path | None = None) -> Generator[sqlite3.Connection, None, None]:
    """Context manager yielding a thread-safe SQLite connection with foreign keys and WAL enabled."""
    target_path = db_path or get_db_path()
    # Ensure directory exists
    target_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(
        str(target_path),
        check_same_thread=False,
        timeout=10.0,
    )
    conn.row_factory = sqlite3.Row

    try:
        # Enable Write-Ahead Logging and Foreign Key constraints
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        yield conn
        conn.commit()
    except Exception as exc:
        conn.rollback()
        logger.error(f"Database transaction error: {exc}")
        raise
    finally:
        conn.close()


def init_db(db_path: Path | None = None) -> List[str]:
    """Initialize SQLite database and execute schema DDL.

    Returns the list of table names created or verified.
    """
    target_path = db_path or get_db_path()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Initializing SQLite database at: {target_path}")

    with get_db_connection(target_path) as conn:
        conn.executescript(SCHEMA_SQL)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
        )
        tables = [row["name"] for row in cursor.fetchall()]

    # Seed deterministic demo records if empty
    try:
        from app.services.data_service import seed_demo_data
        seed_demo_data(target_path)
    except Exception as exc:
        logger.warning(f"Demo data seeding during init_db skipped/failed: {exc}")

    logger.info(f"Database initialized successfully with {len(tables)} tables: {', '.join(tables)}")
    return tables


def check_db_health(db_path: Path | None = None) -> Dict[str, Any]:
    """Ping database and inspect table status for health checks."""
    target_path = db_path or get_db_path()
    try:
        with get_db_connection(target_path) as conn:
            cursor = conn.execute("SELECT 1 AS ping;")
            ping_result = cursor.fetchone()
            if not ping_result or ping_result["ping"] != 1:
                return {
                    "connected": False,
                    "error": "Database ping returned unexpected value",
                    "database_path": str(target_path),
                    "table_count": 0,
                    "tables": [],
                }

            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
            )
            tables = [row["name"] for row in cursor.fetchall()]

            return {
                "connected": True,
                "error": None,
                "database_path": str(target_path),
                "table_count": len(tables),
                "tables": tables,
            }
    except Exception as exc:
        logger.warning(f"Database health check failed: {exc}")
        return {
            "connected": False,
            "error": str(exc),
            "database_path": str(target_path),
            "table_count": 0,
            "tables": [],
        }
