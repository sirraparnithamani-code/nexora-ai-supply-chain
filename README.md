# NEXORA AI — Intelligent, Resilient Supply Chain Management

> **GDGoC Agentic AI Hackathon Project**  
> An autonomous multi-agent decision support and optimization platform designed to safeguard manufacturing operations during critical supplier disruptions. Tagline: *Intelligent, Resilient Supply Chain Management*.

---

## 1. Project Objective

The objective of this project is to build an intelligent, multi-agent supply chain resilience platform capable of autonomously responding to a sudden **seven-day shutdown of a critical manufacturing supplier**.

By deploying a team of four specialized domain AI agents coordinated by a central orchestrator, the system:
- Rapidly evaluates the multi-dimensional impact of the disruption across customer demand, warehouse inventory, alternate suppliers, and transportation logistics.
- Formulates and solves a mathematical optimization model using **Google OR-Tools** to balance trade-offs among costs, lead times, and service levels.
- Compares three distinct planning paradigms (Baseline Business-as-Usual, Heuristic Rule-Based, and Agentic Mathematical Optimization).
- Delivers an intuitive **What-If Dashboard** for scenario simulation and KPI evaluation.
- Implements a **Human-in-the-Loop** governance workflow requiring explicit planner approval before executing mitigation strategies.

---

## 2. Problem Statement

Modern manufacturing operations rely heavily on lean, Just-in-Time (JIT) supply chains. While JIT minimizes warehouse holding costs, it leaves manufacturers critically vulnerable to unexpected disruptions. 

When a sole-source or Tier-1 supplier abruptly halts operations for **seven days** (due to equipment breakdowns, severe weather, labor strikes, or quality recalls):
1. **Production Halts & Stockouts:** Safety stocks deplete rapidly, causing factory assembly lines to idle.
2. **Revenue Loss & SLA Penalties:** High-priority customer orders are delayed, triggering contract penalties and damaged customer trust.
3. **Siloed & Sluggish Response:** Traditional supply chain replanning relies on disjointed spreadsheets and days of cross-departmental coordination, resulting in delayed decisions.
4. **Sub-optimal Knee-Jerk Fixes:** Uncoordinated expediting often leads to exorbitant premium freight costs or ordering excess inventory from unvetted suppliers.

Manufacturers urgently need an **agentic AI architecture** paired with **rigorous mathematical optimization** that can assess enterprise-wide impacts within seconds and recommend optimal, cost-efficient recovery actions.

---

## 3. Planned Technology Stack

The project separates the user-facing web dashboard and the computational backend into distinct, modular layers:

| Layer | Technology | Role & Purpose |
| :--- | :--- | :--- |
| **Frontend** | **React** + **Vite** | Modern, responsive single-page application for simulation controls, metrics, and planner review. |
| **Visualization** | **Recharts** | Interactive timeline charts, inventory burn-down visualizations, and multi-scenario trade-off graphs. |
| **Backend** | **Python** + **FastAPI** | High-performance asynchronous REST API hosting agent workflows and simulation endpoints. |
| **Optimization** | **Google OR-Tools** | Mixed-Integer Linear Programming (MILP) / Constraint Programming (CP-SAT) for optimal allocation and scheduling. |
| **Data Processing** | **pandas** | Tabular data manipulation, Bill of Materials (BOM) explosion, and metrics calculation. |
| **Database** | **SQLite** | Lightweight, zero-configuration relational database storing scenarios, audit logs, and approval states. |

---

## 4. High-Level Workflow

The end-to-end resilient decision loop follows five sequential stages:

```
[ 1. Disruption Alert: 7-Day Supplier Outage ]
                     │
                     ▼
[ 2. Parallel Assessment by 4 Specialized Agents ]
   ├── Demand Agent         (Order priorities, customer SLAs, stockout risks)
   ├── Inventory Agent      (Stock levels, BOM explosion, safety stock runway)
   ├── Supplier-Risk Agent  (Alternate suppliers, capacity, risk ratings)
   └── Logistics Agent      (Freight lanes, transit speeds, expedited costs)
                     │
                     ▼
[ 3. Synthesis & Optimization by Coordinator Agent ]
   ├── Collects structured agent insights
   ├── Runs Google OR-Tools optimization engine
   └── Generates 3 Comparative Planning Scenarios
                     │
                     ▼
[ 4. Interactive What-If Dashboard & Evaluation ]
   ├── Side-by-side KPI comparison (Costs, Fulfillment Rate, Recovery Time)
   └── Scenario simulation parameter adjustments
                     │
                     ▼
[ 5. Human Planner Approval Gate ]
   └── Planner reviews, edits, or approves optimal action plan for execution
```

1. **Disruption Trigger:** A 7-day supplier shutdown event is detected or injected into the system.
2. **Parallel Agent Assessment:** Four specialized AI agents concurrently analyze domain-specific datasets (orders, warehouses, qualified vendors, freight routes).
3. **Optimization & Planning Synthesis:** The Coordinator Agent aggregates domain findings and feeds them into the Google OR-Tools solver to produce optimal mitigation actions alongside baseline and heuristic baselines.
4. **Interactive Dashboard Review:** Planners explore the results via an interactive dashboard displaying trade-off metrics and timeline projections.
5. **Human Approval Gate:** The human planner inspects the recommended purchase orders and freight choices, with full authority to approve, adjust, or reject the plan.

---

## 5. Repository Structure

```
supply-chain-resilience/
├── backend/                    # Python & FastAPI backend service
│   ├── app/
│   │   ├── agents/             # Autonomous Domain AI Agents & Orchestrator
│   │   │   ├── base.py                 # Abstract BaseAgent with latency telemetry
│   │   │   ├── demand_agent.py         # Demand forecasting, tier prioritization & SLA penalties
│   │   │   ├── inventory_agent.py      # BOM explosion, runway auditing & stockout projection
│   │   │   ├── supplier_risk_agent.py  # Outage tracking & alternate vendor qualification
│   │   │   ├── logistics_agent.py      # Multi-modal freight evaluation & transit speed
│   │   │   └── coordinator_agent.py    # Central multi-agent orchestrator & decision synthesis
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── health.py           # Health check & ping endpoints with DB connectivity
│   │   │       └── agents.py           # REST endpoints for individual agents & coordinator
│   │   ├── models/             # Relational domain models & enums
│   │   │   └── supply_chain.py
│   │   ├── schemas/            # Pydantic request/response validation schemas
│   │   │   ├── health.py
│   │   │   └── agents.py
│   │   ├── services/           # Data services & pandas extractors
│   │   │   └── data_service.py         # Relational queries, BOM extraction & seed data
│   │   ├── config.py           # App configuration, environment loading & CORS settings
│   │   ├── database.py         # SQLite connection pooling, WAL mode & DDL schema
│   │   └── main.py             # FastAPI application factory & global middleware
│   ├── .env.example            # Environment variables configuration template
│   ├── requirements.txt        # Backend dependencies
│   └── run.py                  # Convenience entry point for running Uvicorn server
├── frontend/                   # Modern React + Vite + Recharts Dashboard
│   ├── src/
│   │   ├── components/         # Reusable UI cards, tables, header, sidebar & icons
│   │   │   ├── Header.jsx              # Status bar, outage indicator & planner profile
│   │   │   ├── Sidebar.jsx             # Compact navigation & NEXORA AI branding
│   │   │   ├── Icons.jsx               # Lightweight SVG icons (including Indian Rupee ₹)
│   │   │   ├── KpiCard.jsx             # Human-friendly metric cards with trend indicators
│   │   │   ├── DisruptionAlert.jsx     # Active 7-day supplier outage banner
│   │   │   ├── PlanningComparison.jsx  # Side-by-side 3-approach comparison cards
│   │   │   └── ScenarioControlPanel.jsx# Interactive what-if disruption sliders
│   │   ├── views/              # 9 human-friendly operational & intelligence views
│   │   │   ├── OverviewView.jsx        # Executive summary, 7-day chart & approval queue
│   │   │   ├── NetworkView.jsx         # SCM multi-echelon flow (Supplier → Factory → Customer)
│   │   │   ├── InventoryView.jsx       # Available stock vs. safety buffer bar chart
│   │   │   ├── DemandView.jsx          # 7-day customer order book & contractual SLAs
│   │   │   ├── SupplierRiskView.jsx    # Vendor capacity & delivery lead time matrix
│   │   │   ├── LogisticsView.jsx       # Multi-modal freight trade-off & shipment tracker
│   │   │   ├── ScenarioSimulatorView.jsx# Disruption stress-testing & trajectory re-solve
│   │   │   ├── OptimizationView.jsx    # Best Recovery Plan allocations & cost breakdown
│   │   │   └── ApprovalsView.jsx       # Planner Authorization Gate & immutable audit log
│   │   ├── mockData.js         # Coherent synthetic dataset (Parker Hannifin scenario)
│   │   ├── utils/formatters.js # Indian number & currency (₹) formatting utilities
│   │   ├── services/apiService.js# Axios/Fetch integration with FastAPI backend
│   │   ├── App.jsx             # Root layout & view router
│   │   ├── main.jsx            # React 18 DOM mount point
│   │   └── index.css           # Clean light theme design system tokens & styles
│   ├── package.json            # Node.js dependencies
│   └── vite.config.js          # Vite config with backend proxy on /api
├── data/                       # Relational database persistence
│   └── supply_chain.db         # Auto-initialized SQLite database
├── tests/                      # Comprehensive test suite (36 tests)
│   ├── test_health.py          # Database & configuration verification
│   ├── test_demand_agent.py    # Demand agent forecast & SLA exposure tests
│   ├── test_inventory_agent.py # BOM explosion & stockout runway tests
│   ├── test_supplier_risk_agent.py # Outage impact & alternate capacity tests
│   ├── test_logistics_agent.py # Freight corridors & deadline feasibility tests
│   ├── test_coordinator_agent.py # Multi-agent orchestration & synthesis tests
│   └── test_agent_api.py       # FastAPI REST contract integration tests
├── .gitignore                  # Exclusions for Python, Node, database, and env files
├── README.md                   # Project overview, workflow, and Windows run guide (this file)
└── PROJECT_PLAN.md             # Detailed engineering plan, mathematical formulation & milestones
```

---

## 6. Synthetic Manufacturing Demonstration Dataset

> **Disclaimer:** *Synthetic Demo Data — Not Actual Company Data.*  
> This dataset provides an illustrative discrete manufacturing scenario inspired by the general operations of **Parker Hannifin India Pvt. Ltd., Hyderabad** (Hydraulic components, industrial valves, and sealing systems). It is designed to illustrate multi-agent supply chain resilience with realistic operational trade-offs.

### 6.1. Currency Standard: Indian Rupees (₹)
All monetary metrics across the entire application—inventory valuations, purchase costs, freight rates, contract delay penalties, recovery expenses, and comparative savings—are modeled and displayed in **Indian Rupees (₹)** using standard Indian numbering formatting:
- **Examples:** `₹1,25,000`, `₹4,12,000`, `₹42.0 lakh`, `₹14.80 lakh`.
- **Zero Dollar ($) Representation:** The application exclusively uses ₹ throughout all UI components, charts, backend summaries, and reports.

### 6.2. Disruption Scenario Parameters
- **Disrupted Sole-Source Supplier:**  
  *Kalyani Precision Forgings (SUP-001)* located in Chakan, Pune, Maharashtra. An unscheduled high-temperature induction furnace coil breakdown causes an abrupt **7-day plant shutdown**, halting deliveries of forged valve spool castings (`CMP-MCU-9000`).
- **Manufacturing Plant:**  
  *Hyderabad Main Facility (Cherlapally)*, feeding two critical assembly lines:
  - *Line 1:* Automated Valve Assembly Line (Electro-Hydraulic Proportional Valves `FG-ROBOT-01`).
  - *Line 2:* Precision Hydraulic Cylinder Line (Heavy-Duty Hydraulic Cylinders `FG-CTRL-02`).
- **Inventory Balance & Stockout Cliff:**  
  - Initial on-hand stock: **2,400 units**.
  - Safety stock threshold: **600 units**.
  - Daily consumption: **580 units/day**.
  - **Stockout Cliff:** Safety stock breached on Day 3; complete stock exhaustion on **Day 4**, threatening line stoppages and **₹42.0 lakh** in sales contract exposure.
- **Qualified Alternate Suppliers:**  
  1. *Sundaram Precision Hydraulics (SUP-002, Ambattur, Chennai)*: 450 units/day capacity, 2-day lead time via Dedicated Air Cargo charter (+18% price premium).
  2. *Kirloskar Precision Castings (SUP-003, Peenya, Bengaluru)*: 320 units/day capacity, 4-day lead time via NH-44 Expedited Road Transport (+12% price premium).
- **Customer Priority Tiers & Contractual SLAs:**  
  - *Gold Tier (100% Protected):* Larsen & Toubro Construction (L&T) and Tata Motors Commercial Vehicles (daily SLA delay penalty: ₹1.8 lakh/day).
  - *Silver Tier:* Mahindra & Mahindra Farm Equipment and BEML Mining & Defence.
  - *Standard Tier:* Escorts Kubota Agri Machinery.

---

## 7. Quick Start & Windows Setup Guide

### 7.1. Prerequisites
- **Python:** 3.10 or higher (Python 3.14 tested and supported)
- **Node.js:** v18 or higher (with npm)
- **Terminal:** Windows PowerShell

### 7.2. Step 1: Set Up Python Backend Virtual Environment

Open Windows PowerShell in the project root directory (`supply-chain-resilience`):

```powershell
# Create virtual environment (if not already created)
python -m venv backend\.venv

# Activate virtual environment in PowerShell
.\backend\.venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r backend\requirements.txt
```

### 7.3. Step 2: Run Backend Automated Tests

Verify that all 36 unit and integration tests pass:

```powershell
backend\.venv\Scripts\pytest
```

Expected output:
```text
======================= 36 passed, 2 warnings in 2.54s ========================
```

### 7.4. Step 3: Start the FastAPI Backend Server

In your PowerShell terminal:

```powershell
backend\.venv\Scripts\python backend\run.py
```

The backend server launches on `http://127.0.0.1:8000`:
- **Interactive Swagger Documentation:** `http://127.0.0.1:8000/docs`
- **Health Check Endpoint:** `http://127.0.0.1:8000/api/health`
- **Multi-Agent Roster:** `http://127.0.0.1:8000/api/agents/info`

### 7.5. Step 4: Install Dependencies & Run React Frontend Dashboard

In a **second Windows PowerShell terminal**, navigate to the `frontend` directory:

```powershell
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```

The frontend dashboard opens immediately at:
```text
  VITE v5.4.21  ready in 320 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

To build and verify the production bundle:
```powershell
npm run build
```

---

## 8. Interactive API Endpoints

Once the FastAPI backend server is running, the following endpoints are available:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | API status, metadata, and links to documentation. |
| `GET` | `/api/health` | Comprehensive health check returning SQLite connectivity, table counts, and CORS origins. |
| `GET` | `/api/health/ping` | Ultra-fast liveness ping returning `{"ping": "pong"}`. |
| `GET` | `/api/agents/info` | Roster and operational status of all four domain agents and the coordinator. |
| `POST` | `/api/agents/demand` | Demand Agent: 7-day forecasting, customer priority tiers, and SLA penalty calculations. |
| `POST` | `/api/agents/inventory` | Inventory Agent: BOM explosion, stock runway auditing, and stockout timeline. |
| `POST` | `/api/agents/supplier-risk` | Supplier-Risk Agent: 7-day outage assessment, alternate capacity, and vendor surcharges. |
| `POST` | `/api/agents/logistics` | Logistics Agent: Freight corridor evaluation, transit speeds, and deadline feasibility. |
| `POST` | `/api/agents/coordinator` | Coordinator Agent: Full multi-agent orchestration, shortage synthesis, and actionable recovery plan. |
| `POST` | `/api/optimization/solve` | Optimization Engine: Direct Google OR-Tools MILP solver with dual-sourcing allocation and 3-way benchmarking. |
| `POST` | `/api/simulator/run` | What-If Simulator: Recalculates KPIs, trajectory, and recovery plans for dynamic disruption parameters. |
| `GET` | `/api/approvals` | Planner Approvals: Current authorization queue and SQLite persistent audit log history. |
| `POST` | `/api/approvals/{id}/decide` | Planner Decision: Authorize or decline PO / freight actions and record in SQLite audit logs. |
| `POST` | `/api/approvals/reset` | Planner Approvals Reset: Restores default pending queue state. |
| `GET` | `/api/data/summary` | Synthetic Dataset Summary: Complete catalog counts and metadata. |
| `GET` | `/api/data/suppliers` | Suppliers Master: Disrupted primary and qualified alternative suppliers. |
| `GET` | `/api/data/components` | Components Master: SKUs, stock levels, holding costs, and daily usage. |
| `GET` | `/api/data/orders` | Customer Sales Orders: Priority tiers, quantities, due dates, and SLA delay penalties. |
| `GET` | `/docs` | Interactive Swagger UI (OpenAPI specification & live testing). |

---

## 9. Human-Friendly Frontend Control Tower

The frontend is specifically designed for manufacturing operations managers using clear, plain-language terminology:

| Technical Concept | Human-Friendly Interface Name | View / Component |
| :--- | :--- | :--- |
| Optimization Results | **Best Recovery Plan** | `OptimizationView.jsx` |
| Supplier-Risk Agent | **Supplier Risk** | `SupplierRiskView.jsx` |
| Scenario Simulator | **Try a What-If Scenario** | `ScenarioSimulatorView.jsx` |
| Human-in-the-Loop | **Planner Approval** | `ApprovalsView.jsx` |
| Solver Latency | **Calculation Time** | Metrics display across views |

### Overview Page Structure (Requirement-Compliant Order):
1. **Header & Active Disruption Alert:** Page title, subtitle, live backend badge, 7-day Pune outage indicator, and lead planner profile.
2. **Key KPI Cards:** Customer Orders Fulfilled, Inventory Remaining, Production Lines at Risk, Estimated Recovery Cost (in ₹), and Supplier Risk Score.
3. **7-Day Demand vs. Production Line Chart:** Recharts visualization comparing baseline demand vs. unmitigated output cliff vs. stabilized recovery output.
4. **Critical Components & Supplier Status Table:** Real-time stock, safety buffer, daily burn rate, and vendor operational status.
5. **Recommended Recovery Plan Card:** Plain-language summary explaining *What Happened*, *Why It Matters*, and *Recommended Action*.
6. **Three-Plan Comparison:** Side-by-side cards comparing Baseline (No Action), Rule-Based Recovery, and Best Recovery Plan.
7. **Pending Planner Approvals:** Action items ready for planner authorization with instant status feedback and audit logging.

---

## 10. Project Milestones & Verification Status

- [x] **Milestone 1: Project Foundation & Architecture** (Modular directory layout, `.gitignore`, `PROJECT_PLAN.md`)
- [x] **Milestone 1.5: FastAPI Backend & Health Probes** (FastAPI app factory, SQLite WAL mode, health check endpoints)
- [x] **Milestone 2: Relational Schemas & Deterministic Data Engine** (SQLite schema, BOM explosion, data loaders in `data_service.py`)
- [x] **Milestone 3: Specialized Domain AI Agents** (Demand, Inventory, Supplier-Risk, Logistics agents with full Pydantic contracts)
- [x] **Milestone 4: Coordinator Agent & Multi-Agent Synthesis** (Central orchestrator, inter-agent trade-off resolution, shortage and recovery synthesis)
- [x] **Milestone 5: Multi-Agent REST API Endpoints** (Async FastAPI routes for individual agents, coordinator, optimizer, and approvals)
- [x] **Milestone 6: React + Vite + Recharts Dashboard Redesign** (Clean light theme, compact cards, NEXORA AI branding, 9 views, Indian Rupee ₹ formatting)
- [x] **Milestone 7: What-If Simulation & Human-in-the-Loop Governance** (Dynamic disruption sliders, dual-modal split routing, planner approvals with SQLite audit trail)
- [x] **Milestone 8: Automated Verification & Documentation** (60 passing pytest tests, clean Vite production build, comprehensive README.md)

