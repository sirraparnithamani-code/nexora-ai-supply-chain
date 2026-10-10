"""API route handlers for Supply Chain Data & Catalog exploration.

Provides endpoints to inspect suppliers, components, BOM relationships,
and customer sales orders from SQLite.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List
from fastapi import APIRouter

from app.database import get_db_connection
from app.services.data_service import (
    DEMO_DISCLAIMER,
    get_bom_dataframe,
    get_components_dataframe,
    get_cost_assumptions,
    get_sales_orders_dataframe,
    get_suppliers_dataframe,
    run_data_quality_checks,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/data", tags=["Supply Chain Data"])


@router.get(
    "/summary",
    summary="Supply Chain Dataset Summary",
    description="Returns full synthetic manufacturing dataset (Suppliers, Components, Products, BOM, Orders) from SQLite.",
)
async def get_data_summary() -> Dict[str, Any]:
    """Fetch complete supply chain entity catalog."""
    suppliers_df = get_suppliers_dataframe()
    components_df = get_components_dataframe()
    bom_df = get_bom_dataframe()
    orders_df = get_sales_orders_dataframe()

    return {
        "disclaimer": DEMO_DISCLAIMER,
        "currency": "INR (₹)",
        "location": "Parker Hannifin India Pvt. Ltd., Hyderabad",
        "counts": {
            "suppliers": len(suppliers_df),
            "components": len(components_df),
            "bill_of_materials": len(bom_df),
            "orders": len(orders_df),
        },
        "suppliers": suppliers_df.to_dict(orient="records"),
        "components": components_df.to_dict(orient="records"),
        "bill_of_materials": bom_df.to_dict(orient="records"),
        "sales_orders": orders_df.to_dict(orient="records"),
    }


@router.get(
    "/suppliers",
    summary="List Suppliers",
    description="Returns all active and disrupted suppliers with capacity and lead times.",
)
async def list_suppliers() -> List[Dict[str, Any]]:
    """Fetch suppliers list."""
    df = get_suppliers_dataframe()
    return df.to_dict(orient="records")


@router.get(
    "/components",
    summary="List Components",
    description="Returns all inventory components, on-hand stocks, and safety stock thresholds.",
)
async def list_components() -> List[Dict[str, Any]]:
    """Fetch components list."""
    df = get_components_dataframe()
    return df.to_dict(orient="records")


@router.get(
    "/orders",
    summary="List Sales Orders",
    description="Returns open customer contracts with priority tiers and SLA penalty rates.",
)
async def list_orders() -> List[Dict[str, Any]]:
    """Fetch sales orders list."""
    df = get_sales_orders_dataframe()
    return df.to_dict(orient="records")


@router.get(
    "/quality",
    summary="Automated Data Quality & Schema Audit",
    description="Runs automated data-quality checks across SQLite relational tables (referential integrity, bounds, completeness).",
)
async def check_data_quality() -> Dict[str, Any]:
    """Execute automated data quality checks."""
    return run_data_quality_checks()


@router.get(
    "/assumptions",
    summary="Documented Cost Assumptions & Parameters",
    description="Returns documented unit costs, holding costs, expedited freight rates, and SLA penalty matrices.",
)
async def list_cost_assumptions() -> Dict[str, Any]:
    """Fetch documented cost assumptions."""
    return get_cost_assumptions()

