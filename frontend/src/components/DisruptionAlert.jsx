import React from 'react';
import { AlertTriangleIcon, ClockIcon, DollarIcon, SlidersIcon } from './Icons';

export const DisruptionAlert = ({ alert, onNavigateToSimulator }) => {
  return (
    <div className="disruption-alert" role="alert">
      <div className="alert-main">
        <div className="alert-icon-box">
          <AlertTriangleIcon className="w-4 h-4" />
        </div>
        <div>
          <div className="alert-heading">
            <span>{alert.title}</span>
            <span className="badge-outage-duration">{alert.durationDays}-DAY SHUTDOWN</span>
          </div>

          <p className="alert-details-text">
            <strong>{alert.supplierName} ({alert.tier})</strong> in {alert.location} reported an
            unscheduled outage impacting critical component <strong>{alert.affectedPart} ({alert.sku})</strong>.
            {' '}{alert.reason}
          </p>

          <div className="alert-chips-row">
            <span className="alert-chip">
              <ClockIcon className="w-3.5 h-3.5 text-blue" />
              <span>Stock Runway: <strong>{alert.safetyStockRunwayDays} Days (Stockout on Day {alert.stockoutDay})</strong></span>
            </span>
            <span className="alert-chip">
              <DollarIcon className="w-3.5 h-3.5 text-blue" />
              <span>Revenue at Risk: <strong>{alert.potentialRevenueAtRisk}</strong></span>
            </span>
            <span className="alert-chip">
              <span>Orders Impacted: <strong>{alert.impactedOrdersCount} Customer Orders</strong></span>
            </span>
            <span className="alert-chip">
              <span>Affected Lines: <strong>Valve Line 1 & Cylinder Line 2</strong></span>
            </span>
          </div>
        </div>
      </div>

      {onNavigateToSimulator && (
        <div className="alert-action-btn">
          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={onNavigateToSimulator}
          >
            <SlidersIcon className="w-3.5 h-3.5" />
            <span>Try a What-If Scenario</span>
          </button>
        </div>
      )}
    </div>
  );
};
