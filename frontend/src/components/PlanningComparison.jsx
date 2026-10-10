import React from 'react';
import { CheckCircleIcon, SparklesIcon } from './Icons';

export const PlanningComparison = ({ approaches, selectedApproach, onSelectApproach }) => {
  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title-group">
          <h2>
            <SparklesIcon className="w-4 h-4 text-blue" />
            <span>Three Planning Approaches Compared</span>
          </h2>
          <p>
            Evaluation of the 7-day supplier shutdown across three recovery strategies: Reactive Baseline, Rule-Based Recovery, and Best Recovery Plan.
          </p>
        </div>
      </div>

      <div className="approaches-grid">
        {approaches.map((approach) => {
          const isSelected = selectedApproach === approach.id;

          return (
            <div
              key={approach.id}
              className={`approach-card ${approach.isRecommended ? 'recommended' : ''}`}
              style={{
                borderColor: isSelected ? 'var(--blue-primary)' : undefined,
                boxShadow: isSelected ? '0 0 0 2px var(--blue-primary)' : undefined,
              }}
            >
              <div>
                <div className="approach-top">
                  <span className={`badge ${approach.isRecommended ? 'badge-info' : 'badge-warning'}`}>
                    {approach.badge}
                  </span>
                  {approach.isRecommended && (
                    <span style={{ fontSize: '10.5px', color: '#0369A1', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '3px' }}>
                      <CheckCircleIcon className="w-3 h-3" /> Recommended
                    </span>
                  )}
                </div>

                <h3 className="approach-title">{approach.name}</h3>
                <div className="approach-cost">{approach.totalCost}</div>
                <div className="approach-cost-label">Total Estimated Disruption Cost</div>

                <div className="approach-stats">
                  <div className="stat-row">
                    <span className="stat-label">Order Fulfillment Rate</span>
                    <span
                      className="stat-value"
                      style={{
                        color:
                          parseFloat(approach.fulfillmentRate) >= 90
                            ? 'var(--success)'
                            : 'var(--danger)',
                      }}
                    >
                      {approach.fulfillmentRate}
                    </span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Plant Downtime</span>
                    <span className="stat-value">{approach.downtimeDays}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Expedited Freight Spend</span>
                    <span className="stat-value">{approach.freightCost}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">SLA Delay Penalties</span>
                    <span className="stat-value">{approach.penaltyCost}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Projected Order Backlog</span>
                    <span className="stat-value">{approach.backlogUnits}</span>
                  </div>
                </div>

                <p style={{ fontSize: '11.5px', color: 'var(--text-secondary)', marginBottom: '10px', lineHeight: 1.4 }}>
                  <strong>Strategy:</strong> {approach.summary}
                </p>

                <div className="approach-pros-cons">
                  <div className="pro-item">
                    <strong>✓ Advantage:</strong> {approach.pros}
                  </div>
                  <div className="con-item">
                    <strong>✕ Trade-off:</strong> {approach.cons}
                  </div>
                </div>
              </div>

              {onSelectApproach && (
                <div style={{ marginTop: '10px' }}>
                  <button
                    type="button"
                    className={`btn w-full ${
                      approach.isRecommended ? 'btn-primary' : 'btn-secondary'
                    }`}
                    style={{ width: '100%' }}
                    onClick={() => onSelectApproach(approach.id)}
                  >
                    {isSelected ? '✓ Active Plan Selected' : `Select ${approach.badge}`}
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
