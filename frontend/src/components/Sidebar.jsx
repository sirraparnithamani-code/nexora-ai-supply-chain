import React from 'react';
import {
  ApprovalIcon,
  DashboardIcon,
  DemandIcon,
  InventoryIcon,
  LogisticsIcon,
  NetworkIcon,
  OptimizationIcon,
  SimulatorIcon,
  SupplierIcon,
} from './Icons';

export const navItems = [
  { id: 'overview', label: 'Overview', icon: DashboardIcon },
  { id: 'network', label: 'Supply Chain Network', icon: NetworkIcon },
  { id: 'inventory', label: 'Inventory', icon: InventoryIcon },
  { id: 'demand', label: 'Demand Forecast', icon: DemandIcon },
  { id: 'supplier-risk', label: 'Supplier Risk', icon: SupplierIcon },
  { id: 'logistics', label: 'Logistics', icon: LogisticsIcon },
  { id: 'simulator', label: 'Try a What-If Scenario', icon: SimulatorIcon },
  { id: 'optimization', label: 'Best Recovery Plan', icon: OptimizationIcon },
  { id: 'approvals', label: 'Planner Approval', icon: ApprovalIcon, badge: 3 },
];

export const Sidebar = ({ activeTab, onSelectTab, isMobileOpen, onCloseMobile, pendingApprovalsCount = 3 }) => {
  return (
    <aside className={`sidebar ${isMobileOpen ? 'mobile-open' : ''}`}>
      {/* Brand Header with attractive Logo */}
      <div className="sidebar-brand">
        <div className="brand-icon-box" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="12 2 2 7 12 12 22 7 12 2" />
            <polyline points="2 17 12 22 22 17" />
            <polyline points="2 12 12 17 22 12" />
          </svg>
        </div>
        <div className="brand-info">
          <span className="brand-name">NEXORA AI</span>
          <span className="brand-tagline">Resilient Manufacturing SCM</span>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="sidebar-nav" aria-label="Main Navigation">
        <div className="nav-section-title">Operations & Network</div>

        {navItems.slice(0, 6).map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;

          return (
            <button
              key={item.id}
              type="button"
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => {
                onSelectTab(item.id);
                if (onCloseMobile) onCloseMobile();
              }}
            >
              <Icon className="nav-item-icon" />
              <span>{item.label}</span>
            </button>
          );
        })}

        <div className="nav-section-title" style={{ marginTop: '6px' }}>
          Decision Intelligence
        </div>

        {navItems.slice(6).map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          const badgeCount = item.id === 'approvals' ? pendingApprovalsCount : item.badge;

          return (
            <button
              key={item.id}
              type="button"
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => {
                onSelectTab(item.id);
                if (onCloseMobile) onCloseMobile();
              }}
            >
              <Icon className="nav-item-icon" />
              <span>{item.label}</span>
              {badgeCount > 0 && <span className="nav-badge">{badgeCount}</span>}
            </button>
          );
        })}
      </nav>

      {/* Sidebar Footer with Synthetic Demo Scenario Indicator */}
      <div className="sidebar-footer">
        <div className="scenario-badge-box">
          <div className="scenario-badge-label">
            <span>Scenario Model</span>
            <span style={{ fontSize: '9px', padding: '1px 5px', background: '#0284C7', color: '#FFF', borderRadius: '4px' }}>
              DEMO
            </span>
          </div>
          <div className="scenario-badge-sub">
            Parker Hannifin India (Hyd)
            <br />
            <span style={{ color: '#64748B' }}>Synthetic Demo Data</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
