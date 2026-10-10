import React from 'react';
import { TrendingDownIcon, TrendingUpIcon } from './Icons';

export const KpiCard = ({
  title,
  value,
  target,
  change,
  trend,
  subtext,
  status = 'info',
  icon,
  explanation,
}) => {
  const getPillStyle = () => {
    switch (status) {
      case 'danger':
        return { bg: 'var(--danger-light)', color: 'var(--danger)' };
      case 'warning':
        return { bg: 'var(--warning-light)', color: 'var(--warning)' };
      case 'success':
        return { bg: 'var(--success-light)', color: 'var(--success)' };
      default:
        return { bg: 'var(--blue-light)', color: 'var(--blue-primary)' };
    }
  };

  const pill = getPillStyle();

  return (
    <div className="kpi-card" title={explanation || subtext}>
      <div className="kpi-top">
        <span className="kpi-label">{title}</span>
        {icon && (
          <div className="kpi-icon-pill" style={{ backgroundColor: pill.bg, color: pill.color }}>
            {icon}
          </div>
        )}
      </div>

      <div className="kpi-value-row">
        <span className="kpi-number">{value}</span>
        {target && <span className="kpi-target">Target: {target}</span>}
      </div>

      <div className="kpi-bottom">
        {change && (
          <span
            className={`kpi-trend ${
              trend === 'down-bad' || trend === 'up-bad'
                ? 'trend-down-bad'
                : 'trend-good'
            }`}
          >
            {trend?.startsWith('up') ? (
              <TrendingUpIcon className="w-3 h-3" />
            ) : (
              <TrendingDownIcon className="w-3 h-3" />
            )}
            {change}
          </span>
        )}
        <span className="kpi-subtext">{subtext}</span>
      </div>
    </div>
  );
};
