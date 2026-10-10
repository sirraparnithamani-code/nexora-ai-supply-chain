import React from 'react';
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import { DisruptionAlert } from '../components/DisruptionAlert';
import {
  AlertTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  DollarIcon,
  InventoryIcon,
  PackageIcon,
  ShieldIcon,
  SparklesIcon,
  TrendingDownIcon,
  TrendingUpIcon,
  TruckIcon,
} from '../components/Icons';
import { KpiCard } from '../components/KpiCard';
import { PlanningComparison } from '../components/PlanningComparison';
import { DEMO_DISCLAIMER } from '../mockData';
import { formatINR } from '../utils/formatters';

export const OverviewView = ({
  alert,
  kpiList,
  sevenDayChartData,
  componentsList,
  approaches,
  selectedApproach,
  onSelectApproach,
  approvalsList,
  onUpdateApprovalStatus,
  onNavigateToTab,
}) => {
  const getKpiIcon = (id) => {
    switch (id) {
      case 'kpi-fulfillment':
        return <ShieldIcon className="w-3.5 h-3.5" />;
      case 'kpi-inventory-remaining':
        return <InventoryIcon className="w-3.5 h-3.5" />;
      case 'kpi-production-at-risk':
        return <AlertTriangleIcon className="w-3.5 h-3.5" />;
      case 'kpi-recovery-cost':
        return <DollarIcon className="w-3.5 h-3.5" />;
      case 'kpi-supplier-risk':
        return <TruckIcon className="w-3.5 h-3.5" />;
      default:
        return <PackageIcon className="w-3.5 h-3.5" />;
    }
  };

  const pendingApprovals = approvalsList.filter((item) => item.status === 'PENDING');

  return (
    <div className="content-body">
      {/* Synthetic Demo Data Banner per Requirement 3 */}
      <div className="demo-banner">
        <div className="demo-banner-content">
          <span className="demo-pill">SYNTHETIC DEMO</span>
          <span>{DEMO_DISCLAIMER}</span>
        </div>
        <span style={{ fontSize: '11px', color: '#0369A1' }}>All currency in Indian Rupees (₹)</span>
      </div>

      {/* 1. Header and Active 7-Day Supplier Outage Alert */}
      <DisruptionAlert
        alert={alert}
        onNavigateToSimulator={() => onNavigateToTab('simulator')}
      />

      {/* 2. Key KPI Cards (Customer Orders Fulfilled, Inventory Remaining, Production at Risk, Recovery Cost, Supplier Risk) */}
      <section>
        <div className="kpi-grid">
          {kpiList.map((kpi) => (
            <KpiCard
              key={kpi.id}
              title={kpi.title}
              value={kpi.value}
              target={kpi.target}
              change={kpi.change}
              trend={kpi.trend}
              subtext={kpi.subtext}
              status={kpi.status}
              explanation={kpi.explanation}
              icon={getKpiIcon(kpi.id)}
            />
          ))}
        </div>
      </section>

      {/* 3. Seven-Day Demand versus Production Line Chart */}
      <section className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h2>
              <PackageIcon className="w-4 h-4 text-blue" />
              <span>7-Day Customer Demand vs. Factory Production</span>
            </h2>
            <p>
              Daily comparison showing unmitigated output cliff on Day 4 vs. stabilized recovery output (Hydraulic Components & Valves).
            </p>
          </div>
          <span className="badge badge-warning">Stockout Deficit: 580 units/day</span>
        </div>

        <div style={{ height: 260, width: '100%' }}>
          <ResponsiveContainer>
            <LineChart
              data={sevenDayChartData}
              margin={{ top: 8, right: 12, left: -10, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis dataKey="day" stroke="#64748B" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748B" fontSize={11} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#FFFFFF',
                  borderRadius: '6px',
                  border: '1px solid #CBD5E1',
                  fontSize: '11.5px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '11.5px', paddingTop: '6px' }} />
              <Line
                type="monotone"
                dataKey="customerDemand"
                name="Customer Demand (Units)"
                stroke="#64748B"
                strokeDasharray="4 4"
                strokeWidth={2}
                dot={{ r: 3 }}
              />
              <Line
                type="monotone"
                dataKey="unmitigatedProduction"
                name="Unmitigated Production (No Recovery)"
                stroke="#DC2626"
                strokeWidth={2.4}
                dot={{ r: 3 }}
              />
              <Line
                type="monotone"
                dataKey="optimizedRecovery"
                name="Best Recovery Plan Output"
                stroke="#0284C7"
                strokeWidth={2.4}
                dot={{ r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* 4. Critical Components and Supplier Status Table */}
      <section className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h2>
              <InventoryIcon className="w-4 h-4 text-blue" />
              <span>Critical Manufacturing Components & Supplier Status</span>
            </h2>
            <p>
              Inventory health, daily usage, and operational status of suppliers feeding Hyderabad production lines.
            </p>
          </div>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => onNavigateToTab('inventory')}
          >
            <span>View All Inventory</span>
          </button>
        </div>

        <div className="table-responsive">
          <table className="compact-table">
            <thead>
              <tr>
                <th>Component SKU</th>
                <th>Description</th>
                <th>Category</th>
                <th>Available Stock</th>
                <th>Safety Stock</th>
                <th>Daily Usage</th>
                <th>Runway</th>
                <th>Primary Supplier</th>
                <th>Supplier Status</th>
              </tr>
            </thead>
            <tbody>
              {componentsList.map((comp) => (
                <tr key={comp.sku}>
                  <td>
                    <span className="sku-code">{comp.sku}</span>
                  </td>
                  <td>
                    <strong>{comp.name}</strong>
                  </td>
                  <td>{comp.category}</td>
                  <td>{comp.currentStock.toLocaleString('en-IN')} units</td>
                  <td>{comp.safetyStock.toLocaleString('en-IN')} units</td>
                  <td>{comp.dailyUsage.toLocaleString('en-IN')} / day</td>
                  <td>
                    <span
                      style={{
                        fontWeight: 600,
                        color:
                          comp.status === 'STOCKOUT_IMMINENT'
                            ? 'var(--danger)'
                            : comp.status === 'MONITORING'
                            ? 'var(--warning)'
                            : 'var(--success)',
                      }}
                    >
                      {comp.runwayDays}
                    </span>
                  </td>
                  <td>{comp.primarySupplier}</td>
                  <td>
                    {comp.supplierStatus.includes('SHUTDOWN') ? (
                      <span className="badge badge-danger">Outage Active</span>
                    ) : comp.supplierStatus.includes('AVAILABLE') ? (
                      <span className="badge badge-info">Alternate Ready</span>
                    ) : (
                      <span className="badge badge-success">Operational</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* 5. Recommended Recovery Plan with Short Plain-Language Explanation */}
      <section className="recommended-plan-card">
        <div className="plan-header">
          <div className="plan-title-area">
            <SparklesIcon className="w-4 h-4 text-blue" />
            <h3>Recommended Recovery Plan: Multi-Sourced Dual Sourcing</h3>
            <span className="plan-tag">AI Decision Engine</span>
          </div>
          <span style={{ fontSize: '12px', fontWeight: 700, color: '#0369A1' }}>
            Estimated Total Cost: ₹4,12,000 (Saves ₹5,33,000 vs Rule-Based)
          </span>
        </div>

        <div className="plan-explanation-grid">
          <div className="explanation-col">
            <h4>What Happened</h4>
            <p>
              7-day unscheduled induction furnace shutdown at Kalyani Precision Forgings (Pune) halts supply of 580 valve spools/day to our Hyderabad plant.
            </p>
          </div>
          <div className="explanation-col">
            <h4>Why It Matters</h4>
            <p>
              Internal stock runs out on Day 4, idling Valve Assembly Line 1 and Cylinder Line 2, and jeopardizing ₹42.0 lakh in customer contracts (L&T and Tata Motors).
            </p>
          </div>
          <div className="explanation-col">
            <h4>Recommended Action</h4>
            <p>
              Issue Emergency PO-8821 for 500 units from Sundaram (Chennai) via Air Cargo (arrives Day 3) + PO-8822 for 350 units from Kirloskar (Bengaluru) via Road Transport (arrives Day 5), while safely drawing 320 buffer units.
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
          <div style={{ fontSize: '11.5px', color: 'var(--text-secondary)' }}>
            <strong>Results:</strong> 96.2% order fulfillment • 0 days factory stoppage • 100% Gold-tier orders delivered on-time.
          </div>
          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={() => onNavigateToTab('optimization')}
          >
            <span>View Full Recovery Plan Details</span>
          </button>
        </div>
      </section>

      {/* 6. Three-Plan Comparison */}
      <section>
        <PlanningComparison
          approaches={approaches}
          selectedApproach={selectedApproach}
          onSelectApproach={onSelectApproach}
        />
      </section>

      {/* 7. Pending Planner Approvals */}
      <section className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h2>
              <ShieldIcon className="w-4 h-4 text-blue" />
              <span>Pending Planner Approvals ({pendingApprovals.length} Action Items)</span>
            </h2>
            <p>
              Authorization required by Lead Operations Planner before dispatching purchase commitments and freight corridors.
            </p>
          </div>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => onNavigateToTab('approvals')}
          >
            <span>Open Planner Approval Center</span>
          </button>
        </div>

        {pendingApprovals.length === 0 ? (
          <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>
            <CheckCircleIcon className="w-4 h-4 text-green" style={{ margin: '0 auto 4px' }} />
            <p style={{ fontWeight: 600 }}>All mitigation purchase orders have been authorized.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {pendingApprovals.map((item) => (
              <div key={item.id} className="approval-item-card">
                <div className="approval-item-header">
                  <div className="approval-item-id">
                    <span>{item.id}</span>
                    <span className="badge badge-info">{item.type}</span>
                    <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>• {item.vendor}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '13px', fontWeight: 800, color: 'var(--text-primary)' }}>
                      {item.totalCommitment}
                    </span>
                    <button
                      type="button"
                      className="btn btn-success btn-sm"
                      onClick={() => onUpdateApprovalStatus(item.id, 'APPROVED')}
                    >
                      <span>Approve</span>
                    </button>
                    <button
                      type="button"
                      className="btn btn-secondary btn-sm"
                      onClick={() => onUpdateApprovalStatus(item.id, 'REJECTED')}
                    >
                      <span>Reject</span>
                    </button>
                  </div>
                </div>

                <div className="approval-metrics-grid">
                  <div className="approval-metric-col">
                    <span className="label">Item & Volume</span>
                    <span className="value">{item.item} ({item.quantity})</span>
                  </div>
                  <div className="approval-metric-col">
                    <span className="label">Freight & Transit</span>
                    <span className="value">{item.shippingMode} ({item.transitTime})</span>
                  </div>
                  <div className="approval-metric-col">
                    <span className="label">Allocation</span>
                    <span className="value">{item.assignedTo}</span>
                  </div>
                </div>

                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  <strong>Why it matters:</strong> {item.whyItMatters}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};
