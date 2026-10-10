import React from 'react';
import {
  AlertTriangleIcon,
  CheckCircleIcon,
  NetworkIcon,
  PackageIcon,
  TruckIcon,
} from '../components/Icons';
import { DEMO_DISCLAIMER, networkNodes } from '../mockData';

export const NetworkView = ({ nodes = networkNodes }) => {
  return (
    <div className="content-body">
      {/* Synthetic Demo Banner */}
      <div className="demo-banner">
        <div className="demo-banner-content">
          <span className="demo-pill">SYNTHETIC DEMO</span>
          <span>{DEMO_DISCLAIMER}</span>
        </div>
        <span style={{ fontSize: '11px', color: '#0369A1' }}>Multi-Echelon Network Model</span>
      </div>

      {/* 1. Clear Simple Flow Diagram: Supplier → Warehouse → Factory → Customer (Requirement 5) */}
      <div className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h2>
              <NetworkIcon className="w-4 h-4 text-blue" />
              <span>Supply Chain Network Flow (Supplier → Warehouse → Factory → Customer)</span>
            </h2>
            <p>
              End-to-end multi-echelon material flow for Parker Hannifin India (Hyderabad plant operations).
            </p>
          </div>
          <span className="badge badge-danger">1 Single-Source Disruption Active</span>
        </div>

        {/* Echelon Flow Diagram */}
        <div className="flow-diagram-wrapper">
          {/* Echelon 1: Suppliers */}
          <div className="flow-node danger">
            <div className="flow-node-title">
              <span className="badge badge-danger">1. Tier-1 & Tier-2 Suppliers</span>
            </div>
            <div style={{ fontSize: '11.5px', marginTop: '4px' }}>
              <div style={{ color: 'var(--danger-text)', fontWeight: 600 }}>
                • Kalyani Forgings (Pune) - SHUTDOWN
              </div>
              <div style={{ color: 'var(--success-text)', fontWeight: 600 }}>
                • Sundaram (Chennai) - Air Backup
              </div>
              <div style={{ color: 'var(--success-text)', fontWeight: 600 }}>
                • Kirloskar (Bengaluru) - Road Backup
              </div>
              <div style={{ color: 'var(--text-secondary)' }}>
                • TVS Sealing & Bharat Sensors
              </div>
            </div>
            <span className="flow-node-sub">Raw Castings & Valve Spools</span>
          </div>

          {/* Arrow */}
          <div className="flow-arrow">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
          </div>

          {/* Echelon 2: Regional Warehouse */}
          <div className="flow-node highlight">
            <div className="flow-node-title">
              <span className="badge badge-info">2. Central Warehouse</span>
            </div>
            <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-primary)', marginTop: '2px' }}>
              Hyderabad Inbound Hub
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
              Cherlapally Logistics Park
            </div>
            <div style={{ fontSize: '11px', color: 'var(--warning-text)', fontWeight: 600 }}>
              Safety Buffer: 600 units
            </div>
            <span className="flow-node-sub">Air Charter & Express Road Inbound</span>
          </div>

          {/* Arrow */}
          <div className="flow-arrow">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
          </div>

          {/* Echelon 3: Manufacturing Facility */}
          <div className="flow-node" style={{ borderColor: 'var(--warning-border)', background: '#FFFDF5' }}>
            <div className="flow-node-title">
              <span className="badge badge-warning">3. Manufacturing Plant</span>
            </div>
            <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-primary)', marginTop: '2px' }}>
              Parker Hannifin India Plant
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
              Patancheru, Hyderabad
            </div>
            <div style={{ fontSize: '11px', color: 'var(--danger-text)', fontWeight: 600 }}>
              • Valve Assembly Line 1 (At Risk)
              <br />
              • Cylinder Assembly Line 2 (At Risk)
            </div>
            <span className="flow-node-sub">580 units/day consumption rate</span>
          </div>

          {/* Arrow */}
          <div className="flow-arrow">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
          </div>

          {/* Echelon 4: Customers */}
          <div className="flow-node" style={{ borderColor: 'var(--success-border)', background: '#F0FDF4' }}>
            <div className="flow-node-title">
              <span className="badge badge-success">4. Key OEM Customers</span>
            </div>
            <div style={{ fontSize: '11.5px', marginTop: '4px' }}>
              <div style={{ color: 'var(--text-primary)', fontWeight: 700 }}>
                • Larsen & Toubro (Gold Tier)
              </div>
              <div style={{ color: 'var(--text-primary)', fontWeight: 700 }}>
                • Tata Motors CV (Gold Tier)
              </div>
              <div style={{ color: 'var(--text-primary)', fontWeight: 700 }}>
                • BHEL Hyderabad (Gold Tier)
              </div>
              <div style={{ color: 'var(--text-secondary)' }}>
                • Mahindra & BEML (Silver Tier)
              </div>
            </div>
            <span className="flow-node-sub">100% Gold Orders Protected by Best Recovery Plan</span>
          </div>
        </div>
      </div>

      {/* 2. Resilience Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
        <div className="card" style={{ padding: '12px 14px' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
            Resilience Score
          </span>
          <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--danger)', marginTop: '4px' }}>
            38 / 100 (High Risk)
          </div>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            Single-source sole vendor bottleneck
          </span>
        </div>

        <div className="card" style={{ padding: '12px 14px' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
            Single Points of Failure
          </span>
          <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--danger)', marginTop: '4px' }}>
            1 Supplier (Kalyani)
          </div>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            Provides forged spool for Lines 1 & 2
          </span>
        </div>

        <div className="card" style={{ padding: '12px 14px' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
            Qualified Alternates
          </span>
          <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--success)', marginTop: '4px' }}>
            2 Pre-Audited Vendors
          </div>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            Chennai & Bengaluru (770 units/day)
          </span>
        </div>

        <div className="card" style={{ padding: '12px 14px' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
            Target Factory Lines
          </span>
          <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--blue-primary)', marginTop: '4px' }}>
            Lines 1 & 2 (Hyderabad)
          </div>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            Daily intake requirement: 580 units
          </span>
        </div>
      </div>

      {/* 3. Network Facility Status Table */}
      <div className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h2>Network Facilities & Operational Status</h2>
            <p>End-to-end mapping across suppliers, logistics nodes, factory lines, and customer hubs.</p>
          </div>
        </div>

        <div className="table-responsive">
          <table className="compact-table">
            <thead>
              <tr>
                <th>Node ID</th>
                <th>Facility Name</th>
                <th>Echelon Role</th>
                <th>Classification</th>
                <th>Location</th>
                <th>Operational Status</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {nodes.map((node) => (
                <tr key={node.id}>
                  <td>
                    <span className="sku-code">{node.id}</span>
                  </td>
                  <td><strong>{node.name}</strong></td>
                  <td>{node.type}</td>
                  <td>{node.tier}</td>
                  <td>{node.location}</td>
                  <td>
                    {node.status === 'SHUTDOWN' ? (
                      <span className="badge badge-danger">Outage Active</span>
                    ) : node.status === 'AT_RISK' ? (
                      <span className="badge badge-warning">Stockout At Risk</span>
                    ) : node.status === 'READY' ? (
                      <span className="badge badge-info">Alternate Ready</span>
                    ) : (
                      <span className="badge badge-success">Operational</span>
                    )}
                  </td>
                  <td style={{ fontSize: '11.5px', color: 'var(--text-secondary)' }}>
                    {node.details}
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
