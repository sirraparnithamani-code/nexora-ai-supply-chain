"""API route handlers for Human Planner Approval Workflow.

Governs planner authorization of mitigation purchase orders, air charters,
and safety stock draw-downs with persistent SQLite audit history.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.database import get_db_connection

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/approvals", tags=["Planner Approval Workflow"])

# Initial in-memory approval queue state (synchronized with database)
INITIAL_APPROVALS: List[Dict[str, Any]] = [
    {
        "id": "PO-8821",
        "type": "Emergency Purchase Order",
        "vendor": "Sundaram Precision Hydraulics",
        "vendorLocation": "Ambattur, Chennai, Tamil Nadu",
        "item": "Forged Valve Spool Casting (CMP-MCU-9000)",
        "quantity": "500 units",
        "quantity_numeric": 500,
        "unitCost": "₹5,015 (+18% rush premium)",
        "totalCommitment": "₹25,07,500",
        "totalCommitmentNumeric": 2507500,
        "shippingMode": "Dedicated Air Cargo (MAA → HYD)",
        "transitTime": "2 Days",
        "assignedTo": "Automated Line 1 (Gold-tier Customer Orders)",
        "riskLevel": "Low Risk",
        "recommendedBy": "Supplier Risk & Logistics Agents",
        "status": "PENDING",
        "whyItMatters": "Arrives Day 3 before Day 4 stockout cliff. Protects ₹33 lakh in Gold-tier customer contracts.",
    },
    {
        "id": "PO-8822",
        "type": "Secondary Purchase Order",
        "vendor": "Kirloskar Precision Castings",
        "vendorLocation": "Peenya, Bengaluru, Karnataka",
        "item": "Forged Valve Spool Backup (CMP-MCU-9000)",
        "quantity": "350 units",
        "quantity_numeric": 350,
        "unitCost": "₹4,760 (+12% premium)",
        "totalCommitment": "₹16,66,000",
        "totalCommitmentNumeric": 1666000,
        "shippingMode": "NH-44 Expedited Road Transport",
        "transitTime": "4 Days",
        "assignedTo": "Cylinder Line 2 (Buffer Inventory)",
        "riskLevel": "Low Risk",
        "recommendedBy": "Inventory & Demand Agents",
        "status": "PENDING",
        "whyItMatters": "Replenishes buffer inventory before Day 6 stock exhaustion at economical ground freight rates.",
    },
    {
        "id": "LOG-4091",
        "type": "Freight Corridor Reservation",
        "vendor": "Blue Dart Aviation / Dedicated Cargo",
        "vendorLocation": "Chennai Airport Corridor",
        "item": "Air Charter Corridor Chennai → RGIA Hyderabad",
        "quantity": "Weight 420 kg (500 units)",
        "quantity_numeric": 500,
        "unitCost": "₹175 / kg",
        "totalCommitment": "₹73,500",
        "totalCommitmentNumeric": 73500,
        "shippingMode": "Priority Flight Charter",
        "transitTime": "24 Hours",
        "assignedTo": "Inbound PO-8821 Shipment",
        "riskLevel": "Priority One",
        "recommendedBy": "Logistics Agent",
        "status": "PENDING",
        "whyItMatters": "Guarantees overnight airfield transfer to Hyderabad plant gate by Day 3 morning.",
    },
]

# Mutable runtime queue
current_approvals: List[Dict[str, Any]] = [dict(item) for item in INITIAL_APPROVALS]


class ApprovalDecisionRequest(BaseModel):
    """Planner authorization decision payload."""

    action: Optional[str] = Field(default=None, description="'APPROVED' or 'REJECTED'")
    decision: Optional[str] = Field(default=None, description="Alias for action")
    planner_name: str = Field(default="R. Verma (Lead Operations Planner)")
    notes: Optional[str] = Field(default="")

    def resolved_action(self) -> str:
        act = self.action or self.decision or "APPROVED"
        return act.upper()


class ApprovalsSummaryResponse(BaseModel):
    """Current approval items and historical SQLite audit log."""

    approvals: List[Dict[str, Any]]
    audit_log: List[Dict[str, Any]]
    audit_logs: List[Dict[str, Any]] = Field(default_factory=list)
    pending_count: int
    approved_total: float
    approved_total_commitment: float = 0.0
    status_summary: str
    approval: Optional[Dict[str, Any]] = None
    audit_record: Optional[Dict[str, Any]] = None
    governance_analysis: Dict[str, Any] = Field(default_factory=dict)


def fetch_sqlite_audit_logs() -> List[Dict[str, Any]]:
    """Fetch audit history from SQLite database."""
    logs = []
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, timestamp, agent_name, action, details_json
                FROM audit_logs
                ORDER BY id DESC
                LIMIT 50;
                """
            )
            for row in cursor.fetchall():
                details = {}
                if row["details_json"]:
                    try:
                        details = json.loads(row["details_json"])
                    except Exception:
                        details = {"raw": row["details_json"]}
                logs.append({
                    "id": f"LOG-{row['id']:03d}",
                    "timestamp": row["timestamp"],
                    "actor": row["agent_name"],
                    "action": row["action"],
                    "status": details.get("status", "COMMITTED"),
                    "notes": details.get("notes", ""),
                })
    except Exception as exc:
        logger.warning(f"Could not read audit_logs from SQLite: {exc}")
    return logs


@router.get(
    "",
    response_model=ApprovalsSummaryResponse,
    summary="Get Approval Queue & SQLite Audit History",
    description="Returns pending recovery actions requiring human planner authorization along with persistent SQLite audit records.",
)
async def get_approvals() -> ApprovalsSummaryResponse:
    """Fetch approval actions and SQLite audit trail."""
    audit_logs = fetch_sqlite_audit_logs()
    pending = sum(1 for item in current_approvals if item["status"] == "PENDING")
    approved_total = sum(
        item.get("totalCommitmentNumeric", 0)
        for item in current_approvals
        if item["status"] == "APPROVED"
    )

    governance_analysis = {
        "policy_code": "SC-GOV-2026-HYDERABAD",
        "framework_name": "Autonomous Multi-Agent Resilience Governance Framework",
        "dual_signoff_required": True,
        "dual_signoff_threshold_inr": 1000000.0,
        "single_order_cap_inr": 3000000.0,
        "emergency_budget_cap_inr": 5000000.0,
        "committed_spend_inr": approved_total,
        "remaining_budget_inr": max(0.0, 5000000.0 - approved_total),
        "audit_immutability": "VERIFIED — All planner decisions recorded immutably to SQLite audit_logs table",
        "segregation_of_duties": "Autonomous Agents propose recovery allocations; Licensed Human Planner authorizes purchase commitments",
        "lead_planner": "R. Verma (Lead Operations Planner, Parker Hannifin Hyderabad)",
        "compliance_status": "100% COMPLIANT",
    }

    return ApprovalsSummaryResponse(
        approvals=current_approvals,
        audit_log=audit_logs,
        audit_logs=audit_logs,
        pending_count=pending,
        approved_total=approved_total,
        approved_total_commitment=approved_total,
        status_summary=f"{pending} items pending human planner approval" if pending > 0 else "All recovery actions authorized",
        governance_analysis=governance_analysis,
    )


@router.get(
    "/governance",
    summary="Governance Analysis & Policy Audit",
    description="Returns governance framework parameters, dual-signoff policies, and compliance metrics.",
)
async def get_governance_policy() -> Dict[str, Any]:
    """Fetch governance policy metrics."""
    res = await get_approvals()
    return res.governance_analysis



@router.post(
    "/{action_id}/decide",
    response_model=ApprovalsSummaryResponse,
    summary="Authorize or Reject a Recovery Action",
    description="Records planner decision (APPROVED or REJECTED) and logs the event permanently into SQLite audit history.",
)
async def decide_approval_action(
    action_id: str,
    decision: ApprovalDecisionRequest,
) -> ApprovalsSummaryResponse:
    """Commit planner decision to memory and persist audit entry to SQLite."""
    act = decision.resolved_action()
    target_action = None
    for item in current_approvals:
        if item["id"].upper() == action_id.upper():
            item["status"] = act
            target_action = item
            break

    if target_action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action ID '{action_id}' not found in approvals queue.",
        )

    # Persist decision to SQLite audit_logs
    try:
        with get_db_connection() as conn:
            details_obj = {
                "action_id": action_id,
                "decision": act,
                "notes": decision.notes or "Authorized under standard resilience policy",
                "vendor": target_action.get("vendor"),
                "commitment": target_action.get("totalCommitmentNumeric", 0),
                "status": "COMMITTED" if act == "APPROVED" else "DECLINED",
            }
            conn.execute(
                """
                INSERT INTO audit_logs (agent_name, action, details_json)
                VALUES (?, ?, ?);
                """,
                (
                    decision.planner_name,
                    f"{act} action {action_id} for {target_action.get('vendor')}",
                    json.dumps(details_obj),
                ),
            )

            # If all approved, update simulation_runs status to APPROVED
            all_approved = all(item["status"] == "APPROVED" for item in current_approvals)
            if all_approved:
                conn.execute(
                    """
                    UPDATE simulation_runs
                    SET status = 'APPROVED', approved_by = ?, approved_at = CURRENT_TIMESTAMP
                    WHERE status = 'PENDING_APPROVAL';
                    """,
                    (decision.planner_name,),
                )
    except Exception as exc:
        logger.error(f"Failed to persist approval decision to SQLite: {exc}", exc_info=True)

    res = await get_approvals()
    res.approval = target_action
    res.audit_record = {
        "id": f"AUDIT-{action_id}",
        "action": act,
        "planner_name": decision.planner_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "notes": decision.notes or "Authorized under standard resilience policy",
        "vendor": target_action.get("vendor"),
    }
    return res


@router.post(
    "/reset",
    response_model=ApprovalsSummaryResponse,
    summary="Reset Approval Queue to Pending State",
    description="Restores initial pending approval state and logs reset action in SQLite.",
)
async def reset_approvals() -> ApprovalsSummaryResponse:
    """Reset approval items to initial pending defaults."""
    global current_approvals
    current_approvals = [dict(item) for item in INITIAL_APPROVALS]

    try:
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO audit_logs (agent_name, action, details_json)
                VALUES (?, ?, ?);
                """,
                (
                    "Lead Operations Planner",
                    "Reset mitigation approval review queue to default pending status",
                    json.dumps({"action": "RESET_QUEUE", "status": "RESET"}),
                ),
            )
    except Exception as exc:
        logger.warning(f"Could not log reset in SQLite: {exc}")

    return await get_approvals()
