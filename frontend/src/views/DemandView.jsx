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

import { DemandIcon, ShieldIcon } from '../components/Icons';
import { customerOrders, DEMO_DISCLAIMER } from '../mockData';
import { formatINR } from '../utils/formatters';

export const DemandView = () => {
  const tierComparison = [
    {
      tier: 'Gold Tier (Contractual SLAs - L&T, Tata Motors)',
      baselineFulfillment: 38,
      heuristicFulfillment: 88,
      optimizedFulfillment: 100,
    },
    {
      tier: 'Silver Tier (Commercial Accounts - Mahindra, BEML)',
      baselineFulfillment: 45,
      heuristicFulfillment: 85,
      optimizedFulfillment: 95,
    },
    {
      tier: 'Standard Tier (Flexible Orders - Escorts)',
      baselineFulfillment: 42,
      heuristicFulfillment: 82,
      optimizedFulfillment: 92,
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
        <span style={{ fontSize: '11px', color: '#0369A1' }}>Customer Demand & SLA Penalties in ₹</span>
      </div>

      {/* 1. Demand & Customer Tier Fulfillment Chart */}
      <div className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h2>
              <DemandIcon className="w-4 h-4 text-blue" />
              <span>Customer Order Fulfillment Rate by Priority Tier (%)</span>
            </h2>
            <p>
              Comparing on-time delivery across customer tiers under Baseline, Rule-Based, and Best Recovery Plan.
            </p>
          </div>
          <span className="badge badge-success">Gold Tier 100% Protected</span>
        </div>

        <div style={{ height: 260, width: '100%' }}>
          <ResponsiveContainer>
            <BarChart data={tierComparison} margin={{ top: 8, right: 12, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis dataKey="tier" stroke="#64748B" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748B" fontSize={11} domain={[0, 100]} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#FFFFFF',
                  borderRadius: '6px',
                  border: '1px solid #CBD5E1',
                  fontSize: '11.5px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                }}
                formatter={(val) => [`${val}%`, 'Fulfillment Rate']}
              />
              <Legend wrapperStyle={{ fontSize: '11.5px', paddingTop: '6px' }} />
              <Bar dataKey="baselineFulfillment" name="Baseline Plan (No Action)" fill="#DC2626" radius={[4, 4, 0, 0]} />
              <Bar dataKey="heuristicFulfillment" name="Rule-Based Recovery" fill="#D97706" radius={[4, 4, 0, 0]} />
              <Bar dataKey="optimizedFulfillment" name="Best Recovery Plan" fill="#0284C7" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 2. Customer Demand Book & SLA Penalty Exposure Table */}
      <div className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h2>Customer Orders Due in 7-Day Disruption Window</h2>
            <p>Customer tier priorities, contract values, and daily contractual SLA penalties in Indian Rupees (₹).</p>
          </div>
        </div>

        <div className="table-responsive">
          <table className="compact-table">
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Customer Name</th>
                <th>Tier</th>
                <th>Finished Product</th>
                <th>Quantity</th>
                <th>Due Date</th>
                <th>Contract Value (₹)</th>
                <th>Daily Delay Penalty (₹/day)</th>
                <th>Order Protection Status</th>
              </tr>
            </thead>
            <tbody>
              {customerOrders.map((ord) => (
                <tr key={ord.orderId}>
                  <td>
                    <span className="sku-code">{ord.orderId}</span>
                  </td>
                  <td><strong>{ord.customer}</strong></td>
                  <td>
                    <span
                      className={`badge ${
                        ord.tier === 'Gold'
                          ? 'badge-warning'
                          : ord.tier === 'Silver'
                          ? 'badge-info'
                          : 'badge-secondary'
                      }`}
                    >
                      {ord.tier} Tier
                    </span>
                  </td>
                  <td>{ord.product}</td>
                  <td>{ord.quantity} units</td>
                  <td><strong>{ord.dueDay}</strong></td>
                  <td><strong>{ord.contractValue}</strong></td>
                  <td>
                    <span style={{ color: 'var(--danger)', fontWeight: 600 }}>
                      {ord.penaltyPerDay}
                    </span>
                  </td>
                  <td>
                    {ord.status.includes('PROTECTED') ? (
                      <span className="badge badge-success">✓ 100% Protected</span>
                    ) : ord.status.includes('ON_SCHEDULE') ? (
                      <span className="badge badge-info">On Schedule</span>
                    ) : (
                      <span className="badge badge-warning">{ord.status}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
