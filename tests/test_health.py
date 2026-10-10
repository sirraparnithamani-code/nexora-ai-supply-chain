"""Unit and integration tests for backend configuration, database initialization, and health checks."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Ensure backend folder is in Python search path
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from starlette.testclient import TestClient

from app.config import get_settings
from app.database import check_db_health, init_db
from app.main import app


class BackendFoundationTestCase(unittest.TestCase):
    """Test suite for backend configuration, database, and API endpoints."""

    def test_config_settings(self) -> None:
        """Verify application configuration loads default attributes correctly."""
        settings = get_settings()
        self.assertEqual(settings.app_name, "AI Agents for Resilient Supply Chain Manufacturing API")
        self.assertEqual(settings.version, "0.1.0")
        self.assertIn("http://localhost:5173", settings.cors_origins)
        self.assertIsNotNone(settings.database_path)

    def test_database_initialization(self) -> None:
        """Verify SQLite database initialization creates all core tables."""
        tables = init_db()
        self.assertIsInstance(tables, list)
        expected_tables = {
            "suppliers",
            "components",
            "products",
            "bill_of_materials",
            "sales_orders",
            "simulation_runs",
            "audit_logs",
        }
        for expected in expected_tables:
            self.assertIn(expected, tables, f"Expected table '{expected}' missing from database")

        health = check_db_health()
        self.assertTrue(health["connected"])
        self.assertGreaterEqual(health["table_count"], len(expected_tables))
        self.assertIsNone(health["error"])

    def test_health_endpoint(self) -> None:
        """Verify GET /api/health returns 200 OK with expected payload schema."""
        with TestClient(app) as client:
            response = client.get("/api/health")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "healthy")
            self.assertEqual(data["version"], "0.1.0")
            self.assertTrue(data["database"]["connected"])
            self.assertGreaterEqual(data["database"]["table_count"], 7)
            self.assertIn("http://localhost:5173", data["cors_allowed_origins"])

    def test_ping_endpoint(self) -> None:
        """Verify GET /api/health/ping returns instant pong."""
        with TestClient(app) as client:
            response = client.get("/api/health/ping")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"ping": "pong", "status": "ok"})

    def test_root_endpoint(self) -> None:
        """Verify GET / root endpoint returns service metadata."""
        with TestClient(app) as client:
            response = client.get("/")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "online")
            self.assertIn("/docs", data["documentation"]["swagger_ui"])

    def test_cors_headers(self) -> None:
        """Verify CORS headers are returned for frontend requests."""
        with TestClient(app) as client:
            headers = {"Origin": "http://localhost:5173"}
            response = client.get("/api/health", headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers.get("access-control-allow-origin"), "http://localhost:5173")


if __name__ == "__main__":
    unittest.main()
