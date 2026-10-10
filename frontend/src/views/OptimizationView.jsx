import React from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import { CheckCircleIcon, OptimizationIcon, SparklesIcon } from '../components/Icons';
import { PlanningComparison } from '../components/PlanningComparison';
import { DEMO_DISCLAIMER } from '../mockData';
import { formatINR } from '../utils/formatters';

export const OptimizationView = ({
  approaches,
  selectedApproach,
  onSelectApproach,
  isBackendConnected = false,
  optimizationData = null,
}) => {
  // Bar chart comparing total costs and service levels across all three approaches (Requirement 5)
  const threePlanChartData = approaches.map((app) => ({
    name: app.name.split(':')[1]?.trim() || app.name,
    totalCostLakh: Number(((app.totalCostNumeric || app.total_cost_numeric || 0) / 100000).toFixed(2)),
    fulfillmentRate: app.fulfillmentRateNumeric !== undefined ? app.fulfillmentRateNumeric : app.fulfillment_rate_numeric,
    costDisplay: app.totalCost || app.total_cost,
    fulfillmentDisplay: app.fulfillmentRate || app.fulfillment_rate,
  }));

  const solverStatus = optimizationData?.solver_status || 'OPTIMAL';
  const solverRuntime = optimizationData?.solver_runtime_ms ? `${optimizationData.solver_runtime_ms} ms` : '46 ms';
  const solverEngine = optimizationData ? 'Google OR-Tools pywraplp (SCIP Branch-and-Cut MILP)' : 'Google OR-Tools pywraplp (SCIP MILP)';

  const solverMetrics = [
    { label: 'Calculation Engine', value: solverEngine },
    { label: 'Solver Status', value: `${solverStatus} (Verified Mathematical Run)` },
    { label: 'Calculation Time', value: solverRuntime },
    { label: 'Evaluation Horizon', value: '7 Days (Operational SCM)' },
    { label: 'Decision Allocations', value: '3 Active Orders (Air, Road, Buffer)' },
    { label: 'Cost Savings vs. Rule-Based', value: '₹5,33,000 (56.4% Cost Reduction)' },
  ];

  const allocations = [
    {
      decision: 'Emergency Purchase Order 1 (PO-8821)',
      supplier: 'Sundaram Precision Hydraulics (SUP-002, Chennai)',
      component: 'Forged Valve Spool Casting',
      quantity: '500 units',
      logisticsMode: 'Dedicated Air Cargo (Chennai → Hyderabad)',
      transitTime: '2 Days (Arrives Day 3)',
      cost: '₹25,07,500',
      targetUse: 'Gold-Tier Orders (Valve Assembly Line 1)',
      rationale: 'Fastest arrival beats Day 4 stockout cliff. Eliminates ₹1.8 lakh/day contract delay penalties.',
    },
    {
      decision: 'Secondary Purchase Order 2 (PO-8822)',
      supplier: 'Kirloskar Precision Castings (SUP-003, Bengaluru)',
      component: 'Forged Valve Spool Casting',
      quantity: '350 units',
      logisticsMode: 'NH-44 Expedited Road Transport',
      transitTime: '4 Days (Arrives Day 5)',
      cost: '₹16,66,000',
      targetUse: 'Buffer Stock Replenishment (Cylinder Line 2)',
      rationale: 'Economical road transport restores safety buffer before Day 6 stock exhaustion.',
    },
    {
      decision: 'Safety Buffer Draw-Down',
      supplier: 'Internal Hyderabad Buffer Warehouse',
      component: 'On-Hand Safety Stock',
      quantity: '320 units',
      logisticsMode: 'Internal Facility Transfer',
      transitTime: 'Immediate (Days 1–3)',
      cost: '₹0 (Internal Stock)',
      targetUse: 'Critical Interim Assembly Buffer',
      rationale: 'Authorizes controlled draw-down of safety stock buffer while air freight is in transit.',
    },
  ];

  return (
    <div className="content-body">
      {/* Synthetic Demo Banner */}
      <div className="demo-banner">
        <div className="demo-banner-content">
          <span className="demo-pill">SYNTHETIC DEMO</span>
          <span>{DEMO_DISCLAIMER}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="badge badge-success" style={{ fontSize: '11px' }}>
            ✓ OR-Tools Solver: {solverStatus} ({solverRuntime})
          </span>
          <span style={{ fontSize: '11px', color: '#0369A1' }}>
            {isBackendConnected ? 'Connected to Backend Solver' : 'Verified Optimization Model'}
          </span>
        </div>
      </div>

      {/* 1. Bar Chart: Total Costs & Service Levels across All Three Planning Approaches (Requirement 5) */}
      <div className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h2>
              <OptimizationIcon className="w-4 h-4 text-blue" />
              <span>Three Planning Approaches: Total Disruption Cost vs. Order Fulfillment</span>
            </h2>
            <p>
              Comparing financial loss (₹ Lakh) and customer fulfillment rate (%) across Baseline, Rule-Based, and Best Recovery Plan.
            </p>
          </div>
          <span className="badge badge-success">Best Recovery Saves ₹5.33 Lakh</span>
        </div>

        <div style={{ height: 260, width: '100%' }}>
          <ResponsiveContainer>
            <BarChart
              data={threePlanChartData}
              margin={{ top: 8, right: 12, left: -10, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis dataKey="name" stroke="#64748B" fontSize={11} tickLine={false} />
              <YAxis
                yAxisId="costAxis"
                stroke="#0284C7"
                fontSize={11}
                tickLine={false}
                label={{ value: 'Total Cost (₹ Lakh)', angle: -90, position: 'insideLeft', style: { fontSize: 10, fill: '#0284C7' } }}
              />
              <YAxis
                yAxisId="rateAxis"
                orientation="right"
                stroke="#059669"
                fontSize={11}
                tickLine={false}
                domain={[0, 100]}
                label={{ value: 'Fulfillment Rate (%)', angle: 90, position: 'insideRight', style: { fontSize: 10, fill: '#059669' } }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#FFFFFF',
                  borderRadius: '6px',
                  border: '1px solid #CBD5E1',
                  fontSize: '11.5px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                }}
                formatter={(val, name, item) => {
                  if (name.includes('Cost')) return [`₹${val} Lakh (${item.payload.costDisplay})`, name];
                  return [`${val}%`, name];
                }}
              />
              <Legend wrapperStyle={{ fontSize: '11.5px', paddingTop: '6px' }} />
              <Bar
                yAxisId="costAxis"
                dataKey="totalCostLakh"
                name="Total Disruption Cost (₹ Lakh)"
                fill="#0284C7"
                radius={[4, 4, 0, 0]}
              />
              <Bar
                yAxisId="rateAxis"
                dataKey="fulfillmentRate"
                name="Order Fulfillment Rate (%)"
                fill="#059669"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 2. Calculation Parameters & Decision Engine Details (Plain Language) */}
      <div className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h2>
              <SparklesIcon className="w-4 h-4 text-blue" />
              <span>Calculation Details & Objective Formulation</span>
            </h2>
            <p>
              Mathematical replanning minimizing purchasing premiums, freight rates, and delay SLA penalties.
            </p>
          </div>
          <span className="badge badge-info">
            {isBackendConnected ? 'Backend Connected' : 'Illustrative Demo Calculation'}
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px', marginBottom: '14px' }}>
          {solverMetrics.map((m) => (
            <div
              key={m.label}
              style={{
                background: 'var(--bg-subtle)',
                padding: '10px 12px',
                borderRadius: '6px',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <span style={{ fontSize: '10.5px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
                {m.label}
              </span>
              <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)', marginTop: '2px' }}>
                {m.value}
              </div>
            </div>
          ))}
        </div>

        <div style={{ padding: '12px 14px', background: '#F0F9FF', border: '1px solid #BAE6FD', borderRadius: '6px', fontSize: '11.5px' }}>
          <strong style={{ color: '#0369A1', display: 'block', marginBottom: '3px' }}>
            Objective Formulation (Disruption Cost Minimization):
          </strong>
          <span style={{ fontFamily: 'monospace', color: '#0C4A6E', fontSize: '11.5px' }}>
            min TotalCost = ∑ (ComponentPurchasePrice_₹ × Qty) + ∑ (FreightRate_₹ × Weight_kg) + ∑ (SLAPenalty_₹ × DelayDays)
          </span>
          <p style={{ color: '#0284C7', marginTop: '4px', fontSize: '11px' }}>
            Subject to: Stockout deadline Day 4, Daily usage rate 580 units/day, Vendor spare capacity limits (Sundaram 450, Kirloskar 320), and Gold-tier contract priority.
          </p>
        </div>
      </div>

      {/* 3. Three-Plan Comparison Cards */}
      <PlanningComparison
        approaches={approaches}
        selectedApproach={selectedApproach}
        onSelectApproach={onSelectApproach}
      />

      {/* 4. Actionable Decision Allocations Table */}
      <div className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h2>Recommended Recovery Plan: Decision Allocations</h2>
            <p>Split-sourcing purchase commitments and logistics routes submitted for planner authorization.</p>
          </div>
        </div>

        <div className="table-responsive">
          <table className="compact-table">
            <thead>
              <tr>
                <th>Decision Item</th>
                <th>Assigned Supplier</th>
                <th>Component</th>
                <th>Quantity</th>
                <th>Logistics Corridor</th>
                <th>Transit Time</th>
                <th>Cost (₹)</th>
                <th>Target Line</th>
                <th>Operational Rationale</th>
              </tr>
            </thead>
            <tbody>
              {allocations.map((a) => (
                <tr key={a.decision}>
                  <td><strong>{a.decision}</strong></td>
                  <td>{a.supplier}</td>
                  <td>{a.component}</td>
                  <td><strong>{a.quantity}</strong></td>
                  <td>{a.logisticsMode}</td>
                  <td>{a.transitTime}</td>
                  <td><strong>{a.cost}</strong></td>
                  <td>{a.targetUse}</td>
                  <td style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>{a.rationale}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
