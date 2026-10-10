import React from 'react';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import { AlertTriangleIcon, CheckCircleIcon, InventoryIcon } from '../components/Icons';
import { componentsCatalog, DEMO_DISCLAIMER } from '../mockData';
import { formatINR } from '../utils/formatters';

export const InventoryView = ({ inventoryData }) => {
  // Bar chart data comparing stock, safety stock, and expected usage per Requirement 5
  const stockComparisonData = componentsCatalog.map((item) => ({
    sku: item.sku,
    name: item.name.length > 20 ? item.name.substring(0, 18) + '...' : item.name,
    fullName: item.name,
    availableStock: item.currentStock,
    safetyStock: item.safetyStock,
    expectedUsage: item.dailyUsage * 4, // 4-day cumulative usage window
    dailyUsage: item.dailyUsage,
  }));

  return (
    <div className="content-body">
      {/* Synthetic Demo Banner */}
      <div className="demo-banner">
        <div className="demo-banner-content">
          <span className="demo-pill">SYNTHETIC DEMO</span>
          <span>{DEMO_DISCLAIMER}</span>
        </div>
        <span style={{ fontSize: '11px', color: '#0369A1' }}>Hyderabad Plant Inventory Buffer</span>
      </div>

      {/* 1. Bar Chart: Stock vs Safety Stock vs Expected Usage (Requirement 5) */}
      <div className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h2>
              <InventoryIcon className="w-4 h-4 text-blue" />
              <span>Inventory Stock, Safety Stock & Expected Usage Comparison</span>
            </h2>
            <p>
              Auditing available stock vs. safety stock thresholds and expected 4-day usage across hydraulic components.
            </p>
          </div>
          <span className="badge badge-danger">CMP-MCU-9000 Stockout Risk</span>
        </div>

        <div style={{ height: 260, width: '100%' }}>
          <ResponsiveContainer>
            <BarChart
              data={stockComparisonData}
              margin={{ top: 8, right: 12, left: -10, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis dataKey="sku" stroke="#64748B" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748B" fontSize={11} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#FFFFFF',
                  borderRadius: '6px',
                  border: '1px solid #CBD5E1',
                  fontSize: '11.5px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                }}
                formatter={(val, name, item) => [
                  `${val.toLocaleString('en-IN')} units`,
                  name,
                ]}
              />
              <Legend wrapperStyle={{ fontSize: '11.5px', paddingTop: '6px' }} />
              <Bar
                dataKey="availableStock"
                name="Available Stock"
                fill="#0284C7"
                radius={[4, 4, 0, 0]}
              />
              <Bar
                dataKey="safetyStock"
                name="Safety Stock Buffer"
                fill="#D97706"
                radius={[4, 4, 0, 0]}
              />
              <Bar
                dataKey="expectedUsage"
                name="Expected Usage (4-Day Window)"
                fill="#DC2626"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 2. Critical Component Burn-Down Runway (CMP-MCU-9000) */}
      <div className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h2>
              <AlertTriangleIcon className="w-4 h-4 text-red" />
              <span>Forged Valve Spool Burn-Down Runway (CMP-MCU-9000)</span>
            </h2>
            <p>
              Trajectory showing unmitigated stock exhaustion on Day 4 vs. stabilized multi-source recovery runway.
            </p>
          </div>
          <span className="badge badge-warning">Buffer Depletion Day 3</span>
        </div>

        <div style={{ height: 240, width: '100%' }}>
          <ResponsiveContainer>
            <AreaChart data={inventoryData} margin={{ top: 8, right: 12, left: -10, bottom: 0 }}>
              <defs>
                <linearGradient id="invStockGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#DC2626" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="#DC2626" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="invRecovGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0284C7" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="#0284C7" stopOpacity={0.0} />
                </linearGradient>
              </defs>
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
                dataKey="safetyStock"
                name="Safety Stock (600 units)"
                stroke="#D97706"
                strokeWidth={2}
                strokeDasharray="4 4"
                dot={false}
              />
              <Area
                type="monotone"
                dataKey="stockLevel"
                name="Disrupted Stock (No Replenishment)"
                stroke="#DC2626"
                fill="url(#invStockGrad)"
                strokeWidth={2}
              />
              <Area
                type="monotone"
                dataKey="recoveryLevel"
                name="Best Recovery Plan Runway"
                stroke="#0284C7"
                fill="url(#invRecovGrad)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 3. Detailed Component Inventory Table */}
      <div className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h2>Component Inventory & Cost Breakdown</h2>
            <p>Unit costs and daily inventory holding costs calculated in Indian Rupees (₹).</p>
          </div>
        </div>

        <div className="table-responsive">
          <table className="compact-table">
            <thead>
              <tr>
                <th>SKU</th>
                <th>Component Name</th>
                <th>Category</th>
                <th>Unit Cost</th>
                <th>Daily Holding Cost</th>
                <th>On-Hand Stock</th>
                <th>Safety Buffer</th>
                <th>Daily Usage</th>
                <th>Runway</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {componentsCatalog.map((c) => (
                <tr key={c.sku}>
                  <td>
                    <span className="sku-code">{c.sku}</span>
                  </td>
                  <td><strong>{c.name}</strong></td>
                  <td>{c.category}</td>
                  <td>{formatINR(c.unitCost)}</td>
                  <td>{formatINR(c.holdingCostDaily)} / day</td>
                  <td>{c.currentStock.toLocaleString('en-IN')} units</td>
                  <td>{c.safetyStock.toLocaleString('en-IN')} units</td>
                  <td>{c.dailyUsage.toLocaleString('en-IN')} / day</td>
                  <td>
                    <span
                      style={{
                        fontWeight: 600,
                        color:
                          c.status === 'STOCKOUT_IMMINENT'
                            ? 'var(--danger)'
                            : c.status === 'MONITORING'
                            ? 'var(--warning)'
                            : 'var(--success)',
                      }}
                    >
                      {c.runwayDays}
                    </span>
                  </td>
                  <td>
                    {c.status === 'STOCKOUT_IMMINENT' ? (
                      <span className="badge badge-danger">Stockout Imminent</span>
                    ) : c.status === 'MONITORING' ? (
                      <span className="badge badge-warning">Monitoring</span>
                    ) : (
                      <span className="badge badge-success">Healthy</span>
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
