"""Supply chain domain types and enumeration definitions.

Defines status constants, planning approach types, and customer tier hierarchies.
"""

from __future__ import annotations

from enum import Enum


class CustomerTier(str, Enum):
    """Customer priority tier for order fulfillment and SLA enforcement."""

    GOLD = "Gold"
    SILVER = "Silver"
    STANDARD = "Standard"


class OrderStatus(str, Enum):
    """Lifecycle status of a customer sales order."""

    OPEN = "OPEN"
    FULFILLED = "FULFILLED"
    BACKLOGGED = "BACKLOGGED"
    DELAYED = "DELAYED"


class PlanningApproach(str, Enum):
    """The three planning paradigms evaluated during a disruption."""

    BASELINE = "baseline"        # Naive / Business-as-Usual
    HEURISTIC = "heuristic"      # Rule-Based Rush Expediting
    OPTIMIZED = "optimized"      # Agentic MILP (Google OR-Tools)


class SimulationStatus(str, Enum):
    """Human-in-the-loop approval status for a generated mitigation plan."""

    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class FreightMode(str, Enum):
    """Available freight transportation modes."""

    STANDARD_GROUND = "Standard Ground"
    EXPEDITED_GROUND = "Expedited Ground"
    AIR_CARGO = "Air Cargo"
