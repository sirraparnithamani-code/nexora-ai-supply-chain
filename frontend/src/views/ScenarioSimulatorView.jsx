import React from 'react';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import {
  AlertTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  DollarIcon,
  ShieldIcon,
  SlidersIcon,
  SparklesIcon,
} from '../components/Icons';
import { ScenarioControlPanel } from '../components/ScenarioControlPanel';
import { DEMO_DISCLAIMER } from '../mockData';
import { formatINR } from '../utils/formatters';

export const ScenarioSimulatorView = ({
  scenarioParams,
  onChangeDuration,
  onChangeDemand,
  onChangeCapacity,
  onChangeInventory,
  onChangeDelay,
  onReset,
  onRunSimulation,
  inventoryData,
  isLiveSimulation = false,
  isCalculating = false,
  simulationResult = null,
}) => {
  const {
    duration = 7,
    demandChange = 0,
    alternateCapacity = 65,
    availableInventory = 2400,
    logisticsDelay = 0,
  } = scenarioParams;

  // Realistically scaled calculations based on Parker Hannifin Hyderabad scenario in INR
  const calculatedRecoveryCost = simulationResult
    ? (simulationResult.planning_approaches?.find((a) => a.id === 'optimized')?.total_cost_numeric || 412000)
    : Math.round(
        412000 +
          (duration - 7) * 48000 +
          demandChange * 3500 -
          (alternateCapacity - 65) * 2200 +
          (2400 - availableInventory) * 60 +
          logisticsDelay * 25000
      );

  const calculatedUnmitigatedLoss = simulationResult
    ? (simulationResult.planning_approaches?.find((a) => a.id === 'baseline')?.total_cost_numeric || 1480000)
    : Math.round(
        1480000 +
          (duration - 7) * 165000 +
          (demandChange > 0 ? demandChange * 12000 : demandChange * 8000) +
          (2400 - availableInventory) * 120 +
          logisticsDelay * 45000
      );

  const calculatedFulfillment = simulationResult
    ? (simulationResult.planning_approaches?.find((a) => a.id === 'optimized')?.fulfillment_rate_numeric || 96.2)
    : Math.min(
        99.5,
        Math.max(
          55.0,
          Number(
            (
              96.2 -
              (duration - 7) * 1.5 -
              demandChange * 0.15 +
              (alternateCapacity - 65) * 0.12 -
              ((2400 - availableInventory) / 500) * 1.2 -
              logisticsDelay * 2.0
            ).toFixed(1)
          )
        )
      );

  const calculatedUnmitigatedFulfillment = simulationResult
    ? (simulationResult.planning_approaches?.find((a) => a.id === 'baseline')?.fulfillment_rate_numeric || 42.5)
    : Math.max(
        20.0,
        Number((42.5 - (duration - 7) * 2.5 - demandChange * 0.2 - ((2400 - availableInventory) / 400) * 2.0).toFixed(1))
      );

  const calculatedDowntime = simulationResult
    ? (simulationResult.planning_approaches?.find((a) => a.id === 'optimized')?.downtime_days_numeric || 0.0)
    : duration > 9 && (alternateCapacity < 50 || availableInventory < 1500)
    ? Number(((duration - 9) * 0.5 + (availableInventory < 1500 ? 1.0 : 0)).toFixed(1))
    : 0.0;

  // Comparison bar chart data per Requirement 5: Current Situation vs Proposed Recovery Plan
  const comparisonData = simulationResult?.comparison_data || [
    {
      metric: 'Order Fulfillment (%)',
      currentSituation: calculatedUnmitigatedFulfillment,
      proposedRecovery: calculatedFulfillment,
      unit: '%',
    },
    {
      metric: 'Downtime (Days)',
      currentSituation: Number((duration * 0.78).toFixed(1)),
      proposedRecovery: calculatedDowntime,
      unit: 'Days',
    },
    {
      metric: 'Total Financial Loss (₹ Lakh)',
      currentSituation: Number((calculatedUnmitigatedLoss / 100000).toFixed(1)),
      proposedRecovery: Number((calculatedRecoveryCost / 100000).toFixed(1)),
      unit: '₹ Lakh',
    },
  ];

  // Dynamic simulation trajectory chart comparing current vs proposed
  const simulatedChartData = simulationResult?.seven_day_trajectory
    ? simulationResult.seven_day_trajectory.map((d) => ({
        day: d.day,
        safetyStock: d.safety_stock || 600,
        currentTrajectory: d.baseline_stock,
        proposedRecovery: d.optimized_stock,
      }))
    : inventoryData.map((d, index) => {
        const dayNum = index + 1;
        let currentStock = d.stockLevel;
        let recoveryStock = d.recoveryLevel;

        if (availableInventory !== 2400) {
          const delta = availableInventory - 2400;
          currentStock = Math.max(0, currentStock + delta);
          recoveryStock = Math.max(0, recoveryStock + delta);
        }

        if (dayNum > duration) {
          currentStock = Math.min(availableInventory, currentStock + 300);
        }
        if (demandChange > 0) {
          currentStock = Math.max(0, currentStock - demandChange * 6);
          recoveryStock = Math.max(0, recoveryStock - demandChange * 3);
        }
        if (alternateCapacity > 65) {
          recoveryStock = Math.min(4000, recoveryStock + (alternateCapacity - 65) * 4);
        }

        return {
          ...d,
          currentTrajectory: currentStock,
          proposedRecovery: recoveryStock,
        };
      });

  return (
    <div className="content-body">
      {/* Synthetic Demo Banner */}
      <div className="demo-banner">
        <div className="demo-banner-content">
          <span className="demo-pill">SYNTHETIC DEMO</span>
          <span>{DEMO_DISCLAIMER}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {simulationResult && (
            <span
              className={`badge ${simulationResult.is_optimal ? 'badge-success' : 'badge-warning'}`}
              style={{ fontSize: '11px' }}
            >
              Google OR-Tools: {simulationResult.solver_status} ({simulationResult.solver_runtime_ms} ms)
            </span>
          )}
          <span style={{ fontSize: '11px', color: '#0369A1' }}>
            {isLiveSimulation ? 'Live FastAPI & OR-Tools Engine' : 'Deterministic Decision Model'}
          </span>
        </div>
      </div>

      {/* 1. Control Panel with Sliders */}
      <ScenarioControlPanel
        duration={duration}
        demandChange={demandChange}
        alternateCapacity={alternateCapacity}
        availableInventory={availableInventory}
        logisticsDelay={logisticsDelay}
        onChangeDuration={onChangeDuration}
        onChangeDemand={onChangeDemand}
        onChangeCapacity={onChangeCapacity}
        onChangeInventory={onChangeInventory}
        onChangeDelay={onChangeDelay}
        onReset={onReset}
        onRunSimulation={onRunSimulation}
        isCalculating={isCalculating}
      />

      {/* Solver Summary Callout if available */}
      {simulationResult?.summary && (
        <div style={{ padding: '10px 14px', background: '#F0F9FF', border: '1px solid #BAE6FD', borderRadius: '6px', fontSize: '11.5px', color: '#0369A1' }}>
          <strong>Solver Execution Summary: </strong>
          <span>{simulationResult.summary}</span>
        </div>
      )}

      {/* 2. Impact Summary Cards (Plain Language) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
        <div className="kpi-card">
          <span className="kpi-label">Proposed Recovery Cost</span>
          <div className="kpi-number" style={{ color: 'var(--blue-primary)', marginTop: '4px' }}>
            {formatINR(calculatedRecoveryCost)}
          </div>
          <span className="kpi-subtext">
            vs. {formatINR(calculatedUnmitigatedLoss)} unmitigated loss
          </span>
        </div>

        <div className="kpi-card">
          <span className="kpi-label">Projected Order Fulfillment</span>
          <div
            className="kpi-number"
            style={{
              color: calculatedFulfillment >= 90 ? 'var(--success)' : 'var(--danger)',
              marginTop: '4px',
            }}
          >
            {calculatedFulfillment}%
          </div>
          <span className="kpi-subtext">
            Current unmitigated: {calculatedUnmitigatedFulfillment}%
          </span>
        </div>

        <div className="kpi-card">
          <span className="kpi-label">Factory Line Downtime</span>
          <div
            className="kpi-number"
            style={{
              color: calculatedDowntime === 0 ? 'var(--success)' : 'var(--danger)',
              marginTop: '4px',
            }}
          >
            {calculatedDowntime} Days
          </div>
          <span className="kpi-subtext">
            Protected by alternate air & road delivery
          </span>
        </div>

        <div className="kpi-card">
          <span className="kpi-label">Cost Savings Achieved</span>
          <div className="kpi-number" style={{ color: 'var(--success)', marginTop: '4px' }}>
            {formatINR(calculatedUnmitigatedLoss - calculatedRecoveryCost)}
          </div>
          <span className="kpi-subtext">Net savings via intelligent replanning</span>
        </div>
      </div>

      {/* 3. Comparison of Current Situation vs Proposed Recovery Plan (Requirement 5) */}
      <div className="charts-grid-2">
        {/* Metric Comparison Bar Chart */}
        <div className="card">
          <div className="card-header">
            <div className="card-title-group">
              <h2>
                <SlidersIcon className="w-4 h-4 text-blue" />
                <span>Current Situation vs. Proposed Recovery Plan</span>
              </h2>
              <p>Key operational and financial metrics evaluated side-by-side.</p>
            </div>
          </div>

          <div style={{ height: 260, width: '100%' }}>
            <ResponsiveContainer>
              <BarChart data={comparisonData} margin={{ top: 8, right: 12, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                <XAxis dataKey="metric" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#FFFFFF',
                    borderRadius: '6px',
                    border: '1px solid #CBD5E1',
                    fontSize: '11.5px',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '11.5px', paddingTop: '6px' }} />
                <Bar
                  dataKey="currentSituation"
                  name="Current Situation (No Action)"
                  fill="#DC2626"
                  radius={[4, 4, 0, 0]}
                />
                <Bar
                  dataKey="proposedRecovery"
                  name="Proposed Recovery Plan"
                  fill="#0284C7"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Dynamic Trajectory Comparison Area Chart */}
        <div className="card">
          <div className="card-header">
            <div className="card-title-group">
              <h2>Simulated Inventory Trajectory</h2>
              <p>14-day stock trajectory under current shutdown vs. proposed recovery plan.</p>
            </div>
          </div>

          <div style={{ height: 260, width: '100%' }}>
            <ResponsiveContainer>
              <AreaChart data={simulatedChartData} margin={{ top: 8, right: 12, left: -10, bottom: 0 }}>
                <defs>
                  <linearGradient id="simCurrGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#DC2626" stopOpacity={0.35} />
                    <stop offset="95%" stopColor="#DC2626" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="simRecovGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0284C7" stopOpacity={0.35} />
                    <stop offset="95%" stopColor="#0284C7" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                <XAxis dataKey="day" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#FFFFFF',
                    borderRadius: '6px',
                    border: '1px solid #CBD5E1',
                    fontSize: '11.5px',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '11.5px', paddingTop: '6px' }} />
                <Line
                  type="monotone"
                  dataKey="safetyStock"
                  name="Safety Buffer (600 units)"
                  stroke="#D97706"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                  dot={false}
                />
                <Area
                  type="monotone"
                  dataKey="currentTrajectory"
                  name="Current Stock Trajectory"
                  stroke="#DC2626"
                  fill="url(#simCurrGrad)"
                  strokeWidth={2}
                />
                <Area
                  type="monotone"
                  dataKey="proposedRecovery"
                  name="Proposed Recovery Stock"
                  stroke="#0284C7"
                  fill="url(#simRecovGrad)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
