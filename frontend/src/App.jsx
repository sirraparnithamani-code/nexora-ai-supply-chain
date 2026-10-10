import React, { useEffect, useState } from 'react';

import { Header } from './components/Header';
import { navItems, Sidebar } from './components/Sidebar';
import {
  componentsCatalog,
  criticalAlert,
  initialApprovals,
  inventoryLevels,
  kpis,
  networkNodes,
  planningApproaches,
  sevenDayDemandVsProduction,
  shipments,
  suppliers,
} from './mockData';
import {
  checkBackendHealth,
  decideApproval,
  fetchApprovals,
  resetApprovals,
  runCoordinatorAssessment,
  runScenarioSimulation,
} from './services/apiService';
import { ApprovalsView } from './views/ApprovalsView';
import { DemandView } from './views/DemandView';
import { InventoryView } from './views/InventoryView';
import { LogisticsView } from './views/LogisticsView';
import { NetworkView } from './views/NetworkView';
import { OptimizationView } from './views/OptimizationView';
import { OverviewView } from './views/OverviewView';
import { ScenarioSimulatorView } from './views/ScenarioSimulatorView';
import { SupplierRiskView } from './views/SupplierRiskView';

export function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const [selectedApproach, setSelectedApproach] = useState('optimized');
  const [scenarioParams, setScenarioParams] = useState({
    duration: 7,
    demandChange: 0,
    alternateCapacity: 65,
    availableInventory: 2400,
    logisticsDelay: 0,
  });
  const [simulationResult, setSimulationResult] = useState(null);
  const [approvalsList, setApprovalsList] = useState(initialApprovals);
  const [auditLogs, setAuditLogs] = useState(null);
  const [feedbackToast, setFeedbackToast] = useState(null);
  const [isBackendConnected, setIsBackendConnected] = useState(false);
  const [isCalculating, setIsCalculating] = useState(false);

  // Probe FastAPI backend health on mount and load SQLite audit data
  useEffect(() => {
    let isMounted = true;
    checkBackendHealth().then((health) => {
      if (isMounted && health.connected) {
        setIsBackendConnected(true);
        fetchApprovals().then((res) => {
          if (isMounted && res.success && res.data) {
            if (res.data.approvals && res.data.approvals.length > 0) {
              setApprovalsList(res.data.approvals);
            }
            if (res.data.audit_logs && res.data.audit_logs.length > 0) {
              setAuditLogs(res.data.audit_logs);
            }
          }
        });
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  const showToast = (message, type = 'success') => {
    setFeedbackToast({ message, type });
    setTimeout(() => setFeedbackToast(null), 3800);
  };

  const handleUpdateApprovalStatus = async (id, newStatus, notes = '') => {
    if (isBackendConnected) {
      try {
        const res = await decideApproval(id, newStatus, notes);
        if (res.success && res.data) {
          const fresh = await fetchApprovals();
          if (fresh.success && fresh.data) {
            setApprovalsList(fresh.data.approvals);
            setAuditLogs(fresh.data.audit_logs);
          }
          showToast(
            `Order ${id} ${newStatus === 'APPROVED' ? 'Authorized' : 'Rejected'} — Recorded to SQLite Audit Trail`,
            newStatus === 'APPROVED' ? 'success' : 'danger'
          );
          return;
        }
      } catch {
        // Fall back to local update
      }
    }

    setApprovalsList((prev) =>
      prev.map((item) => (item.id === id ? { ...item, status: newStatus } : item))
    );
    showToast(
      newStatus === 'APPROVED'
        ? `Order ${id} Authorized by Lead Operations Planner`
        : `Order ${id} Rejected by Planner`,
      newStatus === 'APPROVED' ? 'success' : 'danger'
    );
  };

  const handleApproveAll = async (notes = '') => {
    if (isBackendConnected) {
      const pendingItems = approvalsList.filter((a) => a.status === 'PENDING');
      for (const item of pendingItems) {
        await decideApproval(item.id, 'APPROVED', notes || 'Batch authorized by Lead Operations Planner');
      }
      const fresh = await fetchApprovals();
      if (fresh.success && fresh.data) {
        setApprovalsList(fresh.data.approvals);
        setAuditLogs(fresh.data.audit_logs);
      }
      showToast('All pending purchase orders authorized and committed in SQLite database', 'success');
    } else {
      setApprovalsList((prev) => prev.map((item) => ({ ...item, status: 'APPROVED' })));
      showToast('Batch-approved all remaining pending recovery orders', 'success');
    }
  };

  const handleResetApprovals = async () => {
    if (isBackendConnected) {
      try {
        await resetApprovals();
        const fresh = await fetchApprovals();
        if (fresh.success && fresh.data) {
          setApprovalsList(fresh.data.approvals);
          setAuditLogs(fresh.data.audit_logs);
          showToast('Approvals review queue reset to pending default state in database', 'info');
          return;
        }
      } catch {
        // Fall back
      }
    }
    setApprovalsList(initialApprovals);
    showToast('Approvals review queue reset to pending default state', 'info');
  };

  const handleResetScenario = () => {
    setScenarioParams({
      duration: 7,
      demandChange: 0,
      alternateCapacity: 65,
      availableInventory: 2400,
      logisticsDelay: 0,
    });
    setSimulationResult(null);
    showToast('Simulation parameters restored to baseline 7-day outage', 'info');
  };

  const handleRunSimulation = async () => {
    setIsCalculating(true);
    if (isBackendConnected) {
      try {
        const result = await runScenarioSimulation({
          duration: scenarioParams.duration,
          demandChange: scenarioParams.demandChange,
          alternateCapacity: scenarioParams.alternateCapacity,
          availableInventory: scenarioParams.availableInventory,
          logisticsDelay: scenarioParams.logisticsDelay,
        });
        if (result.success && result.data) {
          setSimulationResult(result.data);
          showToast(
            `What-If simulation recalculated via Google OR-Tools: Status ${result.data.solver_status} in ${result.data.solver_runtime_ms} ms.`,
            'success'
          );
        } else {
          showToast(
            `What-If simulation evaluated: ${scenarioParams.duration}-day outage, ${scenarioParams.demandChange}% demand shift.`,
            'info'
          );
        }
      } catch (err) {
        showToast(`Simulation error: ${err.message}`, 'danger');
      }
    } else {
      showToast(
        `What-If simulation evaluated: ${scenarioParams.duration}-day outage, ${scenarioParams.demandChange}% demand shift, ${scenarioParams.availableInventory} stock.`,
        'info'
      );
    }
    setIsCalculating(false);
    setActiveTab('simulator');
  };

  const pendingApprovalsCount = approvalsList.filter((a) => a.status === 'PENDING').length;
  const currentTabObject = navItems.find((item) => item.id === activeTab) || navItems[0];

  const getTabSubtitle = (tabId) => {
    switch (tabId) {
      case 'overview':
        return 'Overview — Parker Hannifin India (Hyderabad Scenario)';
      case 'network':
        return 'Multi-Tier Sourcing & Distribution Topology';
      case 'inventory':
        return 'Stock, Safety Buffer & Expected Usage Analytics';
      case 'demand':
        return '7-Day Customer Demand Book & Contractual SLAs';
      case 'supplier-risk':
        return 'Vendor Capacity & Delivery Lead Time Evaluation';
      case 'logistics':
        return 'Inbound Freight Corridors & Speed vs. Cost Trade-Offs';
      case 'simulator':
        return 'Interactive Disruption Stress-Testing';
      case 'optimization':
        return 'Multi-Agent Best Recovery Plan & Allocations';
      case 'approvals':
        return 'Planner Decision Governance & Authorization Queue';
      default:
        return 'Intelligent, Resilient Manufacturing Management';
    }
  };

  const activeApproaches = simulationResult?.planning_approaches || planningApproaches;
  const activeKpis = simulationResult?.kpis || kpis;
  const activeAlert = simulationResult?.critical_alert || criticalAlert;

  return (
    <div className="app-container">
      {/* Mobile Backdrop Overlay */}
      <div
        className={`sidebar-overlay ${isMobileSidebarOpen ? 'active' : ''}`}
        onClick={() => setIsMobileSidebarOpen(false)}
      />

      {/* Modern Control Tower Sidebar */}
      <Sidebar
        activeTab={activeTab}
        onSelectTab={(tabId) => setActiveTab(tabId)}
        isMobileOpen={isMobileSidebarOpen}
        onCloseMobile={() => setIsMobileSidebarOpen(false)}
        pendingApprovalsCount={pendingApprovalsCount}
      />

      {/* Main Workspace */}
      <div className="main-wrapper">
        <Header
          currentViewTitle={currentTabObject.label}
          currentViewSubtitle={getTabSubtitle(activeTab)}
          isBackendConnected={isBackendConnected}
          onToggleMobileSidebar={() => setIsMobileSidebarOpen(!isMobileSidebarOpen)}
        />

        {/* Floating Toast Notification */}
        {feedbackToast && (
          <div
            style={{
              position: 'fixed',
              top: '72px',
              right: '20px',
              zIndex: 100,
              background: feedbackToast.type === 'danger' ? '#DC2626' : '#0F2537',
              color: '#FFFFFF',
              padding: '9px 16px',
              borderRadius: '6px',
              boxShadow: '0 4px 14px rgba(0,0,0,0.2)',
              fontSize: '12px',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              animation: 'fadeIn 0.2s ease',
            }}
          >
            <span>{feedbackToast.message}</span>
          </div>
        )}

        {/* View Router */}
        {activeTab === 'overview' && (
          <OverviewView
            alert={activeAlert}
            kpiList={activeKpis}
            sevenDayChartData={sevenDayDemandVsProduction}
            componentsList={componentsCatalog}
            approaches={activeApproaches}
            selectedApproach={selectedApproach}
            onSelectApproach={(id) => {
              setSelectedApproach(id);
              showToast(`Active recovery strategy updated to: ${id.toUpperCase()}`);
            }}
            approvalsList={approvalsList}
            onUpdateApprovalStatus={handleUpdateApprovalStatus}
            onNavigateToTab={(tabId) => setActiveTab(tabId)}
          />
        )}

        {activeTab === 'network' && <NetworkView nodes={networkNodes} />}

        {activeTab === 'inventory' && <InventoryView inventoryData={inventoryLevels} />}

        {activeTab === 'demand' && <DemandView />}

        {activeTab === 'supplier-risk' && <SupplierRiskView suppliersList={suppliers} />}

        {activeTab === 'logistics' && <LogisticsView shipmentsList={shipments} />}

        {activeTab === 'simulator' && (
          <ScenarioSimulatorView
            scenarioParams={scenarioParams}
            onChangeDuration={(val) => setScenarioParams((p) => ({ ...p, duration: val }))}
            onChangeDemand={(val) => setScenarioParams((p) => ({ ...p, demandChange: val }))}
            onChangeCapacity={(val) => setScenarioParams((p) => ({ ...p, alternateCapacity: val }))}
            onChangeInventory={(val) => setScenarioParams((p) => ({ ...p, availableInventory: val }))}
            onChangeDelay={(val) => setScenarioParams((p) => ({ ...p, logisticsDelay: val }))}
            onReset={handleResetScenario}
            onRunSimulation={handleRunSimulation}
            inventoryData={inventoryLevels}
            isLiveSimulation={isBackendConnected}
            isCalculating={isCalculating}
            simulationResult={simulationResult}
          />
        )}

        {activeTab === 'optimization' && (
          <OptimizationView
            approaches={activeApproaches}
            selectedApproach={selectedApproach}
            onSelectApproach={(id) => {
              setSelectedApproach(id);
              showToast(`Active recovery strategy updated to: ${id.toUpperCase()}`);
            }}
            isBackendConnected={isBackendConnected}
            optimizationData={simulationResult}
          />
        )}

        {activeTab === 'approvals' && (
          <ApprovalsView
            approvals={approvalsList}
            auditLogs={auditLogs}
            onUpdateStatus={handleUpdateApprovalStatus}
            onResetApprovals={handleResetApprovals}
            onApproveAll={handleApproveAll}
            isBackendConnected={isBackendConnected}
          />
        )}
      </div>
    </div>
  );
}

export default App;
