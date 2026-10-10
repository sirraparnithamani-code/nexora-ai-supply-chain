import React from 'react';
import { CheckCircleIcon, MenuIcon, ShieldIcon, WifiIcon } from './Icons';

export const Header = ({
  currentViewTitle,
  currentViewSubtitle,
  isBackendConnected,
  onToggleMobileSidebar,
}) => {
  return (
    <header className="top-header">
      <div className="header-left">
        <button
          type="button"
          className="mobile-menu-btn"
          onClick={onToggleMobileSidebar}
          aria-label="Toggle navigation menu"
        >
          <MenuIcon className="w-4 h-4" />
        </button>

        <div className="header-title-group">
          <h1>{currentViewTitle}</h1>
          <p>
            {currentViewSubtitle ||
              'NEXORA AI Control Tower — Resilient Manufacturing Management'}
          </p>
        </div>
      </div>

      <div className="header-right">
        {/* Backend Connectivity Status */}
        <div
          className="badge"
          style={{
            backgroundColor: isBackendConnected ? 'var(--success-light)' : 'var(--bg-subtle)',
            color: isBackendConnected ? 'var(--success-text)' : 'var(--text-muted)',
            border: `1px solid ${isBackendConnected ? 'var(--success-border)' : 'var(--border-subtle)'}`,
            fontSize: '11px',
          }}
          title={isBackendConnected ? 'Connected to FastAPI multi-agent backend' : 'Running on synthetic manufacturing dataset (Backend offline)'}
        >
          <WifiIcon className="w-3 h-3" />
          <span>{isBackendConnected ? 'Backend Live' : 'Demo Dataset'}</span>
        </div>

        {/* 7-Day Supplier Outage Status Indicator */}
        <div className="status-badge-outage" title="7-Day Unscheduled Outage: Kalyani Precision Forgings (Pune)">
          <span className="status-beacon-red" />
          <span>Outage: Day 1 of 7 (Pune Plant)</span>
        </div>

        {/* Planner Profile & Approval Status */}
        <div className="header-planner-badge" title="Planner Approval Authority: Operations Lead">
          <div className="planner-avatar">
            <ShieldIcon className="w-3 h-3" />
          </div>
          <div>
            <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>R. Verma</span>
            <span style={{ color: 'var(--text-muted)', marginLeft: '4px', fontSize: '10.5px' }}>
              • Lead Planner
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
