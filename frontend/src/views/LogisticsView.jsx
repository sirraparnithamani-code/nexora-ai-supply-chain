import React from 'react';
import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';

import { ClockIcon, DollarIcon, LogisticsIcon, TruckIcon } from '../components/Icons';
import { DEMO_DISCLAIMER, shipments } from '../mockData';

export const LogisticsView = ({ shipmentsList = shipments }) => {
  // Shipment status distribution chart data per Requirement 5
  const statusPieData = [
    { name: 'On-Time In-Transit', value: 18, color: '#059669' },
    { name: 'Air Expedited', value: 8, color: '#0284C7' },
    { name: 'Delayed (Outage)', value: 14, color: '#DC2626' },
    { name: 'Awaiting Planner Approval', value: 4, color: '#D97706' },
  ];

  const modes = [
    {
      mode: 'Dedicated Air Cargo (Blue Dart Charter)',
      lane: 'Chennai (MAA) → Hyderabad (HYD)',
      speed: '1–2 Days Transit',
      costPerKg: '₹175 / kg',
      reliability: '98.5%',
      useCase: 'Emergency replenishment for Gold-tier orders to prevent plant shutdown on Day 4.',
      badge: 'Fastest / Priority',
      badgeClass: 'badge-info',
    },
    {
      mode: 'Expedited Road Transport (NH-44 Express)',
      lane: 'Peenya, Bengaluru → Hyderabad Plant',
      speed: '3–4 Days Transit',
      costPerKg: '₹45 / kg',
      reliability: '94.0%',
      useCase: 'Secondary replenishment for buffer stock and non-critical assembly lines.',
      badge: 'Economical / Buffer',
      badgeClass: 'badge-success',
    },
    {
      mode: 'Regular Surface Freight (Stalled Route)',
      lane: 'Chakan, Pune → Hyderabad Plant',
      speed: '5–7 Days Transit',
      costPerKg: '₹28 / kg',
      reliability: '40.0% (Outage)',
      useCase: 'Sole-source supplier halted; freight stalled due to plant shutdown.',
      badge: 'Outage Stalled',
      badgeClass: 'badge-danger',
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
        <span style={{ fontSize: '11px', color: '#0369A1' }}>Multi-Modal Freight Evaluation in ₹</span>
      </div>

      {/* 1. Simple Route Flow Diagram (Requirement 5) */}
      <div className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h2>
              <TruckIcon className="w-4 h-4 text-blue" />
              <span>Multi-Modal Sourcing Corridors & Route Flow</span>
            </h2>
            <p>
              Transit lanes connecting supplier manufacturing hubs in Chennai, Bengaluru, and Pune to Hyderabad Assembly Plant.
            </p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px' }}>
          {/* Corridor 1: Emergency Air */}
          <div
            style={{
              background: '#F0F9FF',
              border: '1px solid #BAE6FD',
              borderRadius: '8px',
              padding: '12px 14px',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span className="badge badge-info">Corridor 1: Priority Air</span>
              <span style={{ fontSize: '11px', color: '#0369A1', fontWeight: 600 }}>2-Day Arrival</span>
            </div>
            <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)' }}>
              Chennai (Sundaram) → RGIA Hyderabad Airport
            </div>
            <p style={{ fontSize: '11.5px', color: '#0369A1', lineHeight: 1.4 }}>
              Dedicated Air Cargo carrying 500 valve spools (PO-8821). Arrives morning of Day 3, safely ahead of the Day 4 factory stockout cliff. Rate: ₹175/kg.
            </p>
          </div>

          {/* Corridor 2: NH-44 Express Ground */}
          <div
            style={{
              background: '#ECFDF5',
              border: '1px solid #A7F3D0',
              borderRadius: '8px',
              padding: '12px 14px',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span className="badge badge-success">Corridor 2: NH-44 Highway</span>
              <span style={{ fontSize: '11px', color: '#065F46', fontWeight: 600 }}>4-Day Arrival</span>
            </div>
            <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)' }}>
              Bengaluru (Kirloskar) → Hyderabad Plant Gate
            </div>
            <p style={{ fontSize: '11.5px', color: '#065F46', lineHeight: 1.4 }}>
              Expedited dedicated road truck carrying 350 valve spools (PO-8822). Arrives Day 5 to restore buffer inventory at low transport rate: ₹45/kg.
            </p>
          </div>

          {/* Corridor 3: Disrupted Corridor */}
          <div
            style={{
              background: '#FEF2F2',
              border: '1px solid #FECACA',
              borderRadius: '8px',
              padding: '12px 14px',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span className="badge badge-danger">Corridor 3: Disrupted Lane</span>
              <span style={{ fontSize: '11px', color: '#991B1B', fontWeight: 600 }}>Halted (+7 Days)</span>
            </div>
            <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)' }}>
              Pune (Kalyani Forgings) → Hyderabad
            </div>
            <p style={{ fontSize: '11.5px', color: '#991B1B', lineHeight: 1.4 }}>
              Regular surface lane stalled due to supplier induction furnace breakdown. Normal shipments suspended until Day 8.
            </p>
          </div>
        </div>
      </div>

      {/* 2. Shipment Status Breakdown & Transportation Modes Grid */}
      <div className="charts-grid-2">
        {/* Shipment Status Donut Chart */}
        <div className="card">
          <div className="card-header">
            <div className="card-title-group">
              <h2>Shipment Status Distribution</h2>
              <p>Active inbound freight orders across Indian regional transport lanes.</p>
            </div>
          </div>

          <div style={{ height: 220, display: 'flex', alignItems: 'center' }}>
            <ResponsiveContainer width="55%" height="100%">
              <PieChart>
                <Pie
                  data={statusPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={45}
                  outerRadius={75}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {statusPieData.map((entry, index) => (
                    <Cell key={`slice-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#FFFFFF',
                    borderRadius: '6px',
                    border: '1px solid #CBD5E1',
                    fontSize: '11.5px',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>

            <div style={{ width: '45%', display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '11.5px' }}>
              {statusPieData.map((item) => (
                <div key={item.name} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: item.color }} />
                    <span style={{ color: 'var(--text-secondary)' }}>{item.name}</span>
                  </span>
                  <strong>{item.value}</strong>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Freight Mode Rates */}
        <div className="card">
          <div className="card-header">
            <div className="card-title-group">
              <h2>Freight Mode Speed vs. Cost Trade-Offs</h2>
              <p>Published carrier rate sheets and estimated transit times.</p>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {modes.map((m) => (
              <div
                key={m.mode}
                style={{
                  background: 'var(--bg-subtle)',
                  borderRadius: '6px',
                  padding: '10px 12px',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <span className={`badge ${m.badgeClass}`}>{m.badge}</span>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{m.reliability} Reliability</span>
                </div>
                <div style={{ fontSize: '12.5px', fontWeight: 700, color: 'var(--text-primary)' }}>
                  {m.mode}
                </div>
                <div style={{ display: 'flex', gap: '14px', fontSize: '11.5px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                    <ClockIcon className="w-3.5 h-3.5 text-blue" /> {m.speed}
                  </span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                    <DollarIcon className="w-3.5 h-3.5 text-blue" /> {m.costPerKg}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 3. Inbound Shipments Tracking Table */}
      <div className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h2>Active Inbound Shipments Tracking</h2>
            <p>Tracking shipments affected by the Pune shutdown and alternate air cargo corridors.</p>
          </div>
        </div>

        <div className="table-responsive">
          <table className="compact-table">
            <thead>
              <tr>
                <th>Shipment ID</th>
                <th>Carrier</th>
                <th>Transit Mode</th>
                <th>Origin Hub</th>
                <th>Destination</th>
                <th>Cargo Contents</th>
                <th>Expected ETA</th>
                <th>Risk</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {shipmentsList.map((shp) => (
                <tr key={shp.id}>
                  <td>
                    <span className="sku-code">{shp.id}</span>
                  </td>
                  <td><strong>{shp.carrier}</strong></td>
                  <td>{shp.mode}</td>
                  <td>{shp.origin}</td>
                  <td>{shp.destination}</td>
                  <td>{shp.items}</td>
                  <td><strong>{shp.eta}</strong></td>
                  <td>
                    <span
                      style={{
                        fontWeight: 600,
                        color:
                          shp.risk === 'High'
                            ? 'var(--danger)'
                            : shp.risk === 'Medium'
                            ? 'var(--warning)'
                            : 'var(--success)',
                      }}
                    >
                      {shp.risk}
                    </span>
                  </td>
                  <td>
                    {shp.status === 'DELAYED' ? (
                      <span className="badge badge-danger">Delayed (+7d)</span>
                    ) : shp.status === 'EXPEDITED' ? (
                      <span className="badge badge-info">Air Expedited</span>
                    ) : shp.status === 'IN_TRANSIT' ? (
                      <span className="badge badge-success">In Transit</span>
                    ) : (
                      <span className="badge badge-warning">Awaiting Approval</span>
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
