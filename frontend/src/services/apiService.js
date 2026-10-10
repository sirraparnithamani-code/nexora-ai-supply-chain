/**
 * API Service for NEXORA AI Multi-Agent Backend
 * Communicates with FastAPI endpoints when available.
 * Transparently indicates whether responses are live from backend or local synthetic models.
 */

const API_BASE = import.meta.env.VITE_API_URL || '/api';
export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
    });
    if (!res.ok) return { connected: false, error: `HTTP ${res.status}` };
    const data = await res.json();
    return { connected: true, data };
  } catch (err) {
    return { connected: false, error: err.message };
  }
}

export async function runCoordinatorAssessment({
  shutdownDurationDays = 7,
  demandChangePct = 0,
  disruptedSupplierId = 'SUP-001',
  targetSku = 'CMP-MCU-9000',
  alternateCapacityFactor = 1.0,
}) {
  try {
    const res = await fetch(`${API_BASE}/agents/coordinator`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({
        shutdown_duration_days: shutdownDurationDays,
        demand_change_pct: demandChangePct,
        disrupted_supplier_id: disruptedSupplierId,
        target_sku: targetSku,
        alternate_capacity_factor: alternateCapacityFactor,
      }),
    });

    if (!res.ok) {
      throw new Error(`Coordinator assessment failed: HTTP ${res.status}`);
    }

    const data = await res.json();
    return { success: true, isLive: true, data };
  } catch (err) {
    console.warn('Backend unavailable, using synthetic demo model:', err.message);
    return { success: false, isLive: false, error: err.message };
  }
}

export async function fetchAgentsInfo() {
  try {
    const res = await fetch(`${API_BASE}/agents/info`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return { success: true, isLive: true, data };
  } catch (err) {
    return { success: false, isLive: false, error: err.message };
  }
}

export async function runScenarioSimulation({
  duration = 7,
  demandChange = 0,
  alternateCapacity = 65,
  availableInventory = 2400,
  logisticsDelay = 0,
}) {
  try {
    const res = await fetch(`${API_BASE}/simulator/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({
        duration: Number(duration),
        demand_change: Number(demandChange),
        alternate_capacity: Number(alternateCapacity),
        available_inventory: Number(availableInventory),
        logistics_delay: Number(logisticsDelay),
      }),
    });

    if (!res.ok) {
      throw new Error(`Scenario simulation failed: HTTP ${res.status}`);
    }

    const data = await res.json();
    return { success: true, isLive: true, data };
  } catch (err) {
    console.warn('Backend simulator unavailable, falling back:', err.message);
    return { success: false, isLive: false, error: err.message };
  }
}

export async function solveOptimization(params = {}) {
  try {
    const res = await fetch(`${API_BASE}/optimization/solve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({
        horizon_days: params.horizonDays || 7,
        shutdown_duration_days: params.shutdownDurationDays || 7,
        initial_inventory: params.initialInventory !== undefined ? params.initialInventory : 2400,
        safety_stock_threshold: params.safetyStockThreshold || 600,
        daily_consumption_rate: params.dailyConsumptionRate || 580.0,
        demand_change_pct: params.demandChangePct || 0.0,
        alternate_capacity_factor: params.alternateCapacityFactor !== undefined ? params.alternateCapacityFactor : 0.65,
        logistics_delay_days: params.logisticsDelayDays || 0,
        target_sku: params.targetSku || 'CMP-MCU-9000',
        disrupted_supplier_id: params.disruptedSupplierId || 'SUP-001',
      }),
    });

    if (!res.ok) {
      throw new Error(`Optimization solve failed: HTTP ${res.status}`);
    }

    const data = await res.json();
    return { success: true, isLive: true, data };
  } catch (err) {
    return { success: false, isLive: false, error: err.message };
  }
}

export async function fetchApprovals() {
  try {
    const res = await fetch(`${API_BASE}/approvals`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return { success: true, isLive: true, data };
  } catch (err) {
    return { success: false, isLive: false, error: err.message };
  }
}

export async function decideApproval(actionId, decision, notes = '', plannerName = 'R. Verma (Lead Operations Planner)') {
  try {
    const res = await fetch(`${API_BASE}/approvals/${actionId}/decide`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({
        decision,
        notes,
        planner_name: plannerName,
      }),
    });

    if (!res.ok) {
      throw new Error(`Decision update failed: HTTP ${res.status}`);
    }

    const data = await res.json();
    return { success: true, isLive: true, data };
  } catch (err) {
    return { success: false, isLive: false, error: err.message };
  }
}

export async function resetApprovals() {
  try {
    const res = await fetch(`${API_BASE}/approvals/reset`, {
      method: 'POST',
      headers: { Accept: 'application/json' },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return { success: true, isLive: true, data };
  } catch (err) {
    return { success: false, isLive: false, error: err.message };
  }
}

export async function fetchDataSummary() {
  try {
    const res = await fetch(`${API_BASE}/data/summary`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return { success: true, isLive: true, data };
  } catch (err) {
    return { success: false, isLive: false, error: err.message };
  }
}

export async function fetchDataQuality() {
  try {
    const res = await fetch(`${API_BASE}/data/quality`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return { success: true, isLive: true, data };
  } catch (err) {
    return { success: false, isLive: false, error: err.message };
  }
}

export async function fetchCostAssumptions() {
  try {
    const res = await fetch(`${API_BASE}/data/assumptions`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return { success: true, isLive: true, data };
  } catch (err) {
    return { success: false, isLive: false, error: err.message };
  }
}

export async function fetchGovernance() {
  try {
    const res = await fetch(`${API_BASE}/approvals/governance`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return { success: true, isLive: true, data };
  } catch (err) {
    return { success: false, isLive: false, error: err.message };
  }
}

