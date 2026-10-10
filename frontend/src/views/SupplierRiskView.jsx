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

import { AlertTriangleIcon, CheckCircleIcon, SupplierIcon } from '../components/Icons';
import { DEMO_DISCLAIMER, suppliers } from '../mockData';

export const SupplierRiskView = ({ suppliersList = suppliers }) => {
  // Chart data comparing supplier capacity and lead times per Requirement 5
  const capacityAndLeadTimeData = suppliersList.map((s) => ({
    name: s.shortName || s.name,
    fullName: s.name,
    capacityDaily: s.capacityDaily,
    maxCapacity: s.maxCapacity,
    leadTimeDays: s.leadTimeDays,
    status: s.status,
  }));

  return (
    <div className="content-body">
      {/* Synthetic Demo Notice */}
      <div className="demo-banner">
        <div className="demo-banner-content">
          <span className="demo-pill">SYNTHETIC DEMO</span>
          <span>{DEMO_DISCLAIMER}</span>
        </div>
        <span style={{ fontSize: '11px', color: '#0369A1' }}>Multi-Vendor Resiliency Matrix</span>
      </div>

      {/* 1. Summary Risk Indicators */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
        <div className="card" style={{ padding: '12px 14px' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>
            PRIMARY OUTAGE RISK
          </span>
          <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--danger)', marginTop: '4px' }}>
            Kalyani Precision (Pune)
          </div>
          <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
            7-Day Induction Furnace Halt
          </span>
        </div>

        <div className="card" style={{ padding: '12px 14px' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>
            QUALIFIED ALTERNATE CAPACITY
          </span>
          <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--success)', marginTop: '4px' }}>
            770 units / day
          </div>
          <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
            Sundaram (450) + Kirloskar (320)
          </span>
        </div>

        <div className="card" style={{ padding: '12px 14px' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>
            DAILY COMPONENT DEFICIT
          </span>
          <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-primary)', marginTop: '4px' }}>
            580 units / day
          </div>
          <span style={{ fontSize: '11px', color: 'var(--success)' }}>
            Covered by Alternate Sourcing (132%)
          </span>
        </div>

        <div className="card" style={{ padding: '12px 14px' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>
            FASTEST BACKUP LEAD TIME
          </span>
          <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--blue-primary)', marginTop: '4px' }}>
            2 Days (Air Freight)
          </div>
          <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
            Chennai to Hyderabad Corridor
          </span>
        </div>
      </div>

      {/* 2. Chart: Comparing Supplier Capacity and Lead Times (Requirement 5) */}
      <div className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h2>
              <SupplierIcon className="w-4 h-4 text-blue" />
              <span>Supplier Spare Capacity & Lead Time Comparison</span>
            </h2>
            <p>
              Evaluating spare daily capacity (units/day) vs. delivery lead times (days) across primary and alternate vendors.
            </p>
          </div>
          <span className="badge badge-info">2 Qualified Alternates Available</span>
        </div>

        <div style={{ height: 260, width: '100%' }}>
          <ResponsiveContainer>
            <BarChart
              data={capacityAndLeadTimeData}
              margin={{ top: 8, right: 12, left: -10, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis dataKey="name" stroke="#64748B" fontSize={11} tickLine={false} />
              <YAxis
                yAxisId="left"
                stroke="#0284C7"
                fontSize={11}
                tickLine={false}
                label={{ value: 'Capacity (Units/Day)', angle: -90, position: 'insideLeft', style: { fontSize: 10, fill: '#0284C7' } }}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                stroke="#D97706"
                fontSize={11}
                tickLine={false}
                domain={[0, 10]}
                label={{ value: 'Lead Time (Days)', angle: 90, position: 'insideRight', style: { fontSize: 10, fill: '#D97706' } }}
              />
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
              <Bar
                yAxisId="left"
                dataKey="capacityDaily"
                name="Available Spare Capacity (Units/Day)"
                fill="#0284C7"
                radius={[4, 4, 0, 0]}
              />
              <Bar
                yAxisId="right"
                dataKey="leadTimeDays"
                name="Delivery Lead Time (Days)"
                fill="#D97706"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 3. Supplier Directory & Qualification Status Table */}
      <div className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h2>Supplier Directory, Risk Ratings & Surcharges</h2>
            <p>
              Pre-qualified sourcing partners for hydraulic components, industrial valves, and sealing products.
            </p>
          </div>
        </div>

        <div className="table-responsive">
          <table className="compact-table">
            <thead>
              <tr>
                <th>Code</th>
                <th>Supplier Name</th>
                <th>Relationship Tier</th>
                <th>Component Supplied</th>
                <th>Facility Location</th>
                <th>Transit Lead Time</th>
                <th>Price Surcharge</th>
                <th>Reliability</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {suppliersList.map((sup) => (
                <tr key={sup.id}>
                  <td>
                    <span className="sku-code">{sup.id}</span>
                  </td>
                  <td><strong>{sup.name}</strong></td>
                  <td>{sup.tier}</td>
                  <td>{sup.component}</td>
                  <td>{sup.location}</td>
                  <td>{sup.leadTime}</td>
                  <td>
                    {sup.priceMultiplier > 1.0 ? (
                      <span style={{ color: 'var(--warning)', fontWeight: 600 }}>
                        +{Math.round((sup.priceMultiplier - 1.0) * 100)}% Rush Premium
                      </span>
                    ) : (
                      <span style={{ color: 'var(--text-muted)' }}>Nominal (0%)</span>
                    )}
                  </td>
                  <td>{sup.reliability}</td>
                  <td>
                    {sup.status === 'SHUTDOWN' ? (
                      <span className="badge badge-danger">Outage Active</span>
                    ) : sup.status === 'ACTIVE_AVAILABLE' ? (
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
      </div>
    </div>
  );
};
