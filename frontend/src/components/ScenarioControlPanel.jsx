import React from 'react';
import { RefreshIcon, SlidersIcon } from './Icons';

export const ScenarioControlPanel = ({
  duration,
  demandChange,
  alternateCapacity,
  availableInventory = 2400,
  logisticsDelay = 0,
  onChangeDuration,
  onChangeDemand,
  onChangeCapacity,
  onChangeInventory,
  onChangeDelay,
  onReset,
  onRunSimulation,
  isCalculating = false,
}) => {
  return (
    <div className="scenario-box">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <h2 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '7px' }}>
            <SlidersIcon className="w-4 h-4 text-blue" />
            <span>Interactive Disruption Simulator — 5 Dynamic Controls</span>
          </h2>
          <p style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>
            Stress-test Hyderabad manufacturing lines under supplier outages, demand volatility, vendor spare capacity, starting stock runway, and freight delays.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button type="button" className="btn btn-secondary btn-sm" onClick={onReset}>
            <RefreshIcon className="w-3.5 h-3.5" />
            <span>Reset Baseline</span>
          </button>
          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={onRunSimulation}
            disabled={isCalculating}
          >
            <span>{isCalculating ? 'Recalculating...' : 'Run What-If Analysis'}</span>
          </button>
        </div>
      </div>

      <div className="scenario-controls-grid">
        {/* Slider 1: Shutdown Duration */}
        <div className="slider-group">
          <div className="slider-top-row">
            <span className="slider-title">Supplier Shutdown Duration:</span>
            <span
              className="slider-val-pill"
              style={{
                backgroundColor: duration >= 10 ? 'var(--danger-light)' : duration >= 7 ? 'var(--warning-light)' : 'var(--blue-light)',
                color: duration >= 10 ? 'var(--danger-text)' : duration >= 7 ? 'var(--warning-text)' : 'var(--blue-primary)',
              }}
            >
              {duration} Days
            </span>
          </div>
          <input
            type="range"
            min="1"
            max="14"
            step="1"
            value={duration}
            onChange={(e) => onChangeDuration(Number(e.target.value))}
            aria-label="Supplier Outage Duration in Days"
          />
          <div className="slider-legend">
            <span>1 Day (Minor)</span>
            <span>7 Days (Baseline)</span>
            <span>14 Days (Severe)</span>
          </div>
        </div>

        {/* Slider 2: Demand Surge / Drop */}
        <div className="slider-group">
          <div className="slider-top-row">
            <span className="slider-title">Customer Demand Shift:</span>
            <span
              className="slider-val-pill"
              style={{
                backgroundColor: demandChange > 0 ? 'var(--danger-light)' : demandChange < 0 ? 'var(--success-light)' : 'var(--bg-subtle)',
                color: demandChange > 0 ? 'var(--danger-text)' : demandChange < 0 ? 'var(--success-text)' : 'var(--text-secondary)',
              }}
            >
              {demandChange > 0 ? `+${demandChange}% Surge` : demandChange < 0 ? `${demandChange}% Drop` : '0% (Nominal)'}
            </span>
          </div>
          <input
            type="range"
            min="-30"
            max="30"
            step="5"
            value={demandChange}
            onChange={(e) => onChangeDemand(Number(e.target.value))}
            aria-label="Customer Demand Shift Percentage"
          />
          <div className="slider-legend">
            <span>-30% Demand</span>
            <span>Baseline (0%)</span>
            <span>+30% Spike</span>
          </div>
        </div>

        {/* Slider 3: Alternate Supplier Capacity */}
        <div className="slider-group">
          <div className="slider-top-row">
            <span className="slider-title">Alternate Supplier Spare Capacity:</span>
            <span
              className="slider-val-pill"
              style={{
                backgroundColor: alternateCapacity >= 65 ? 'var(--success-light)' : 'var(--warning-light)',
                color: alternateCapacity >= 65 ? 'var(--success-text)' : 'var(--warning-text)',
              }}
            >
              {alternateCapacity}% Available
            </span>
          </div>
          <input
            type="range"
            min="20"
            max="100"
            step="5"
            value={alternateCapacity}
            onChange={(e) => onChangeCapacity(Number(e.target.value))}
            aria-label="Alternate Supplier Capacity Percentage"
          />
          <div className="slider-legend">
            <span>20% (Constrained)</span>
            <span>65% (Nominal)</span>
            <span>100% (Full Spare)</span>
          </div>
        </div>

        {/* Slider 4: Available Starting Inventory */}
        <div className="slider-group">
          <div className="slider-top-row">
            <span className="slider-title">Available Starting Inventory:</span>
            <span
              className="slider-val-pill"
              style={{
                backgroundColor: availableInventory >= 2400 ? 'var(--success-light)' : availableInventory >= 1200 ? 'var(--warning-light)' : 'var(--danger-light)',
                color: availableInventory >= 2400 ? 'var(--success-text)' : availableInventory >= 1200 ? 'var(--warning-text)' : 'var(--danger-text)',
              }}
            >
              {availableInventory.toLocaleString('en-IN')} units
            </span>
          </div>
          <input
            type="range"
            min="500"
            max="4000"
            step="100"
            value={availableInventory}
            onChange={(e) => onChangeInventory && onChangeInventory(Number(e.target.value))}
            aria-label="Available Starting Inventory in Units"
          />
          <div className="slider-legend">
            <span>500 (Depleted)</span>
            <span>2,400 (Baseline)</span>
            <span>4,000 (Buffered)</span>
          </div>
        </div>

        {/* Slider 5: Logistics Transit Delay */}
        <div className="slider-group">
          <div className="slider-top-row">
            <span className="slider-title">Optional Freight Transit Delay:</span>
            <span
              className="slider-val-pill"
              style={{
                backgroundColor: logisticsDelay > 0 ? 'var(--warning-light)' : 'var(--success-light)',
                color: logisticsDelay > 0 ? 'var(--warning-text)' : 'var(--success-text)',
              }}
            >
              {logisticsDelay > 0 ? `+${logisticsDelay} Days Delay` : '0 Days (On-Time)'}
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="4"
            step="1"
            value={logisticsDelay}
            onChange={(e) => onChangeDelay && onChangeDelay(Number(e.target.value))}
            aria-label="Optional Logistics Transit Delay in Days"
          />
          <div className="slider-legend">
            <span>0 Days (On-Schedule)</span>
            <span>2 Days (Moderate)</span>
            <span>4 Days (Severe Lane Halt)</span>
          </div>
        </div>
      </div>
    </div>
  );
};
