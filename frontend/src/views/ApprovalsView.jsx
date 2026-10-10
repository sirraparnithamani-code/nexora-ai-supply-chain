import React, { useState } from 'react';
import {
  ApprovalIcon,
  CheckCircleIcon,
  ClockIcon,
  DollarIcon,
  RefreshIcon,
  ShieldIcon,
  XCircleIcon,
} from '../components/Icons';
import { DEMO_DISCLAIMER } from '../mockData';
import { formatINR } from '../utils/formatters';

export const ApprovalsView = ({
  approvals,
  auditLogs = null,
  onUpdateStatus,
  onResetApprovals,
  onApproveAll = null,
  isBackendConnected = false,
}) => {
  const [plannerNotes, setPlannerNotes] = useState('');
  const [localAuditLog, setLocalAuditLog] = useState([
    {
      id: 'LOG-001',
      timestamp: 'Today at 09:14 AM',
      actor: 'Decision Engine',
      action: 'Formulated Best Recovery Plan with 3 actionable PO/logistics items totaling ₹42,47,000.',
      status: 'INITIATED',
    },
    {
      id: 'LOG-002',
      timestamp: 'Today at 09:15 AM',
      actor: 'R. Verma (Lead Operations Planner)',
      action: 'Opened mitigation review queue for 7-day Kalyani Forgings supplier shutdown.',
      status: 'UNDER_REVIEW',
    },
  ]);

  const activeAuditLog = auditLogs && auditLogs.length > 0 ? auditLogs : localAuditLog;

  const handleApprove = (id) => {
    onUpdateStatus(id, 'APPROVED', plannerNotes);
    if (!auditLogs) {
      const newLog = {
        id: `LOG-00${localAuditLog.length + 1}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        actor: 'R. Verma (Lead Operations Planner)',
        action: `Approved action ${id} with note: "${plannerNotes || 'Authorized under standard resilience policy'}"`,
        status: 'COMMITTED',
      };
      setLocalAuditLog([newLog, ...localAuditLog]);
    }
  };

  const handleReject = (id) => {
    onUpdateStatus(id, 'REJECTED', plannerNotes);
    if (!auditLogs) {
      const newLog = {
        id: `LOG-00${localAuditLog.length + 1}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        actor: 'R. Verma (Lead Operations Planner)',
        action: `Rejected action ${id}. Flagged for parameter recalculation. Note: "${plannerNotes || 'Declined'}"`,
        status: 'DECLINED',
      };
      setLocalAuditLog([newLog, ...localAuditLog]);
    }
  };

  const handleApproveAll = () => {
    if (onApproveAll) {
      onApproveAll(plannerNotes);
    } else {
      approvals.forEach((item) => {
        if (item.status === 'PENDING') {
          onUpdateStatus(item.id, 'APPROVED', plannerNotes);
        }
      });
      if (!auditLogs) {
        const newLog = {
          id: `LOG-00${localAuditLog.length + 1}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          actor: 'R. Verma (Lead Operations Planner)',
          action: 'Batch-approved all remaining pending recovery purchase orders (₹42,47,000 total commitment).',
          status: 'BATCH_COMMITTED',
        };
        setLocalAuditLog([newLog, ...localAuditLog]);
      }
    }
  };

  const pendingCount = approvals.filter((a) => a.status === 'PENDING').length;
  const approvedTotal = approvals
    .filter((a) => a.status === 'APPROVED')
    .reduce((sum, item) => sum + (item.totalCommitmentNumeric || 0), 0);

  return (
    <div className="content-body">
      {/* Synthetic Demo Banner */}
      <div className="demo-banner">
        <div className="demo-banner-content">
          <span className="demo-pill">SYNTHETIC DEMO</span>
          <span>{DEMO_DISCLAIMER}</span>
        </div>
        <span style={{ fontSize: '11px', color: '#0369A1' }}>All commitments in Indian Rupees (₹)</span>
      </div>

      {/* 1. Header Banner */}
      <div className="card" style={{ background: 'linear-gradient(135deg, #F0F9FF 0%, #FFFFFF 100%)', border: '1px solid #BAE6FD' }}>
        <div className="card-header" style={{ borderBottomColor: '#E0F2FE' }}>
          <div className="card-title-group">
            <h2>
              <ShieldIcon className="w-4 h-4 text-blue" />
              <span>Planner Approval Center</span>
            </h2>
            <p>
              Autonomous agents propose mitigation purchase orders and air charters; planner authorization is required before financial commitment.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={onResetApprovals}
            >
              <RefreshIcon className="w-3.5 h-3.5" />
              <span>Reset Review Queue</span>
            </button>
            {pendingCount > 0 && (
              <button
                type="button"
                className="btn btn-primary btn-sm"
                onClick={handleApproveAll}
              >
                <CheckCircleIcon className="w-3.5 h-3.5" />
                <span>Authorize All Pending Orders</span>
              </button>
            )}
          </div>
        </div>

        {/* Review Queue Metrics */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px' }}>
          <div style={{ background: '#FFFFFF', padding: '10px 12px', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
            <span style={{ fontSize: '10.5px', color: 'var(--text-muted)', fontWeight: 600 }}>PENDING ACTIONS</span>
            <div style={{ fontSize: '18px', fontWeight: 800, color: pendingCount > 0 ? 'var(--warning)' : 'var(--success)' }}>
              {pendingCount} Orders Awaiting Approval
            </div>
          </div>
          <div style={{ background: '#FFFFFF', padding: '10px 12px', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
            <span style={{ fontSize: '10.5px', color: 'var(--text-muted)', fontWeight: 600 }}>APPROVED FINANCIAL COMMITMENT</span>
            <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--blue-primary)' }}>
              {formatINR(approvedTotal)}
            </div>
          </div>
          <div style={{ background: '#FFFFFF', padding: '10px 12px', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
            <span style={{ fontSize: '10.5px', color: 'var(--text-muted)', fontWeight: 600 }}>PLANNER AUTHORITY</span>
            <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)', marginTop: '4px' }}>
              R. Verma (Lead Operations Planner)
            </div>
            <span style={{ fontSize: '10.5px', color: 'var(--success)' }}>• Full Signing Authorization</span>
          </div>
        </div>
      </div>

      {/* 2. Planner Decision Notes Input */}
      <div className="card" style={{ padding: '12px 14px' }}>
        <label htmlFor="plannerNotes" style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
          Planner Authorization Memo / Instructions (Applies to next approval action):
        </label>
        <input
          id="plannerNotes"
          type="text"
          value={plannerNotes}
          onChange={(e) => setPlannerNotes(e.target.value)}
          placeholder="e.g. Authorized under contingency budget; coordinate expedited gate clearance at Hyderabad plant."
          style={{
            width: '100%',
            padding: '7px 10px',
            borderRadius: '6px',
            border: '1px solid var(--border-medium)',
            fontSize: '12px',
            color: 'var(--text-primary)',
            outline: 'none',
          }}
        />
      </div>

      {/* 3. Detailed Approval Queue Cards */}
      <div className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h2>Actionable Purchase Orders & Freight Reservations Queue</h2>
            <p>Review supplier terms, unit costs with rush surcharges, and arrival timelines.</p>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {approvals.map((item) => (
            <div
              key={item.id}
              className="approval-item-card"
              style={{
                borderColor:
                  item.status === 'APPROVED'
                    ? 'var(--success-border)'
                    : item.status === 'REJECTED'
                    ? 'var(--danger-border)'
                    : 'var(--border-subtle)',
                backgroundColor:
                  item.status === 'APPROVED'
                    ? '#F0FDF4'
                    : item.status === 'REJECTED'
                    ? '#FEF2F2'
                    : 'var(--bg-surface)',
              }}
            >
              <div className="approval-item-header">
                <div className="approval-item-id">
                  <span>{item.id}</span>
                  <span className="badge badge-info">{item.type}</span>
                  <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>• {item.vendor}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '14px', fontWeight: 800, color: 'var(--text-primary)' }}>
                    {item.totalCommitment}
                  </span>
                  {item.status === 'PENDING' ? (
                    <>
                      <button
                        type="button"
                        className="btn btn-success btn-sm"
                        onClick={() => handleApprove(item.id)}
                      >
                        <CheckCircleIcon className="w-3.5 h-3.5" />
                        <span>Authorize</span>
                      </button>
                      <button
                        type="button"
                        className="btn btn-secondary btn-sm"
                        onClick={() => handleReject(item.id)}
                      >
                        <XCircleIcon className="w-3.5 h-3.5" />
                        <span>Reject</span>
                      </button>
                    </>
                  ) : item.status === 'APPROVED' ? (
                    <span className="badge badge-success">✓ Authorized by Planner</span>
                  ) : (
                    <span className="badge badge-danger">✕ Rejected</span>
                  )}
                </div>
              </div>

              <div className="approval-metrics-grid">
                <div className="approval-metric-col">
                  <span className="label">Item & Volume</span>
                  <span className="value">{item.item} ({item.quantity})</span>
                </div>
                <div className="approval-metric-col">
                  <span className="label">Unit Price & Surcharge</span>
                  <span className="value">{item.unitCost}</span>
                </div>
                <div className="approval-metric-col">
                  <span className="label">Transit Mode & Time</span>
                  <span className="value">{item.shippingMode} ({item.transitTime})</span>
                </div>
                <div className="approval-metric-col">
                  <span className="label">Factory Allocation</span>
                  <span className="value">{item.assignedTo}</span>
                </div>
              </div>

              <div style={{ fontSize: '11.5px', color: 'var(--text-secondary)' }}>
                <strong>Why it matters:</strong> {item.whyItMatters}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 4. Planner Decision Audit Trail */}
      <div className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h2>Governance & Planner Audit Trail</h2>
            <p>Chronological log of planner authorizations and system replanning events.</p>
          </div>
        </div>

        <div className="table-responsive">
          <table className="compact-table">
            <thead>
              <tr>
                <th>Log ID</th>
                <th>Time</th>
                <th>Actor</th>
                <th>Action & Decision Details</th>
                <th>Governance State</th>
              </tr>
            </thead>
            <tbody>
              {activeAuditLog.map((log) => (
                <tr key={log.id}>
                  <td>
                    <span className="sku-code">{log.id}</span>
                  </td>
                  <td>{log.timestamp}</td>
                  <td><strong>{log.actor}</strong></td>
                  <td>{log.action}</td>
                  <td>
                    <span
                      className={`badge ${
                        log.status.includes('COMMITTED')
                          ? 'badge-success'
                          : log.status.includes('DECLINED')
                          ? 'badge-danger'
                          : 'badge-info'
                      }`}
                    >
                      {log.status}
                    </span>
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
