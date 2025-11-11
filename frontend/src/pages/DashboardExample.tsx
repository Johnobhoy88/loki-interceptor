/**
 * Dashboard Example Page
 * Comprehensive example showing all visualization components
 */

import React, { useState, useRef } from 'react';
import {
  Download,
  FileImage,
  FileText,
  Copy,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  BarChart3,
} from 'lucide-react';
import {
  ComplianceGauge,
  RiskTrendChart,
  RiskHeatmap,
  ModuleRadarChart,
  GateStatusPieChart,
} from '@/components/charts';
import { StatCard, ProgressIndicator } from '@/components/dashboard';
import { ComplianceTimeline } from '@/components/visualization';
import {
  useRiskTrendData,
  useModuleRadarData,
  useHeatmapData,
  useComplianceScore,
  useGateStatusBreakdown,
} from '@/hooks/useChartData';
import { exportToPNG, exportToPDF, copyToClipboard } from '@/utils/export';
import { RiskLevel, TimelineEvent } from '@/types';

// Mock data for demonstration
const mockTrendData = [
  { date: '2025-11-04', Critical: 3, High: 8, Medium: 15, Low: 24, total: 50 },
  { date: '2025-11-05', Critical: 2, High: 10, Medium: 18, Low: 30, total: 60 },
  { date: '2025-11-06', Critical: 1, High: 7, Medium: 20, Low: 42, total: 70 },
  { date: '2025-11-07', Critical: 2, High: 9, Medium: 19, Low: 35, total: 65 },
  { date: '2025-11-08', Critical: 1, High: 5, Medium: 14, Low: 50, total: 70 },
  { date: '2025-11-09', Critical: 0, High: 6, Medium: 16, Low: 53, total: 75 },
  { date: '2025-11-10', Critical: 1, High: 4, Medium: 15, Low: 60, total: 80 },
  { date: '2025-11-11', Critical: 0, High: 3, Medium: 12, Low: 70, total: 85 },
];

const mockRadarData = [
  { module: 'GDPR', score: 92, fullMark: 100 },
  { module: 'FCA', score: 88, fullMark: 100 },
  { module: 'Tax', score: 95, fullMark: 100 },
  { module: 'Employment', score: 85, fullMark: 100 },
  { module: 'Insurance', score: 90, fullMark: 100 },
];

const mockHeatmapData = [
  { module_id: 'gdpr_uk', gate_id: 'consent', value: 0, label: 'Consent Check' },
  { module_id: 'gdpr_uk', gate_id: 'data_protection', value: 1, label: 'Data Protection' },
  { module_id: 'gdpr_uk', gate_id: 'privacy_policy', value: 0, label: 'Privacy Policy' },
  { module_id: 'fca_uk', gate_id: 'disclosure', value: 2, label: 'Disclosure' },
  { module_id: 'fca_uk', gate_id: 'fair_treatment', value: 0, label: 'Fair Treatment' },
  { module_id: 'fca_uk', gate_id: 'complaints', value: 1, label: 'Complaints' },
  { module_id: 'tax_uk', gate_id: 'vat_threshold', value: 0, label: 'VAT Threshold' },
  { module_id: 'tax_uk', gate_id: 'tax_brackets', value: 0, label: 'Tax Brackets' },
];

const mockGateStatus = [
  { name: 'Pass', value: 234 },
  { name: 'Fail', value: 12 },
  { name: 'Warning', value: 8 },
];

const mockTimelineEvents: TimelineEvent[] = [
  {
    id: '1',
    timestamp: '2025-11-11T10:30:00Z',
    event_type: 'validation',
    title: 'Document Validated',
    description: 'Employment contract validated with 0 critical issues',
    risk_level: RiskLevel.LOW,
  },
  {
    id: '2',
    timestamp: '2025-11-11T09:15:00Z',
    event_type: 'correction',
    title: 'Auto-Correction Applied',
    description: 'Fixed 3 GDPR compliance issues automatically',
    risk_level: RiskLevel.MEDIUM,
  },
  {
    id: '3',
    timestamp: '2025-11-11T08:00:00Z',
    event_type: 'alert',
    title: 'High Risk Detected',
    description: 'Marketing material flagged for FCA review',
    risk_level: RiskLevel.HIGH,
  },
];

export const DashboardExample: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'trends' | 'modules' | 'timeline'>('overview');
  const gaugeRef = useRef<HTMLDivElement>(null);
  const trendRef = useRef<HTMLDivElement>(null);

  const handleExport = async (format: 'png' | 'pdf', ref: React.RefObject<HTMLDivElement>) => {
    if (!ref.current) return;

    try {
      if (format === 'png') {
        await exportToPNG(ref.current, { filename: `compliance-chart-${Date.now()}.png` });
      } else {
        await exportToPDF(ref.current, { filename: `compliance-chart-${Date.now()}.pdf` });
      }
      alert(`Chart exported as ${format.toUpperCase()} successfully!`);
    } catch (error) {
      console.error('Export error:', error);
      alert('Failed to export chart');
    }
  };

  const handleCopy = async (ref: React.RefObject<HTMLDivElement>) => {
    if (!ref.current) return;

    try {
      await copyToClipboard(ref.current);
      alert('Chart copied to clipboard!');
    } catch (error) {
      console.error('Copy error:', error);
      alert('Failed to copy chart');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Compliance Analytics Dashboard
          </h1>
          <p className="text-gray-600">
            Interactive visualization examples for LOKI compliance platform
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Validations"
            value={1248}
            subtitle="Last 30 days"
            trend={{ direction: 'up', value: 12.5, label: 'vs last month' }}
            icon={<BarChart3 size={24} />}
            color="primary"
          />
          <StatCard
            title="Compliance Score"
            value="92%"
            subtitle="Overall performance"
            trend={{ direction: 'up', value: 5.2, label: 'improving' }}
            icon={<TrendingUp size={24} />}
            color="success"
          />
          <StatCard
            title="Critical Issues"
            value={3}
            subtitle="Requires attention"
            trend={{ direction: 'down', value: 45, label: 'vs last week' }}
            icon={<AlertCircle size={24} />}
            color="danger"
          />
          <StatCard
            title="Auto-Corrected"
            value={234}
            subtitle="Issues resolved"
            trend={{ direction: 'up', value: 28, label: 'efficiency up' }}
            icon={<CheckCircle size={24} />}
            color="success"
          />
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-lg mb-8">
          <div className="flex border-b border-gray-200">
            {['overview', 'trends', 'modules', 'timeline'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab as any)}
                className={`px-6 py-4 font-medium capitalize transition-colors ${
                  activeTab === tab
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          <div className="p-8">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-8">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Compliance Gauge */}
                  <div className="bg-gray-50 rounded-lg p-6" ref={gaugeRef}>
                    <div className="flex justify-between items-center mb-4">
                      <h3 className="text-lg font-semibold">Compliance Score</h3>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleCopy(gaugeRef)}
                          className="p-2 hover:bg-gray-200 rounded"
                          title="Copy to clipboard"
                        >
                          <Copy size={18} />
                        </button>
                        <button
                          onClick={() => handleExport('png', gaugeRef)}
                          className="p-2 hover:bg-gray-200 rounded"
                          title="Export as PNG"
                        >
                          <FileImage size={18} />
                        </button>
                        <button
                          onClick={() => handleExport('pdf', gaugeRef)}
                          className="p-2 hover:bg-gray-200 rounded"
                          title="Export as PDF"
                        >
                          <FileText size={18} />
                        </button>
                      </div>
                    </div>
                    <ComplianceGauge score={92} showGrade showPercentage />
                  </div>

                  {/* Gate Status */}
                  <div className="bg-gray-50 rounded-lg p-6">
                    <h3 className="text-lg font-semibold mb-4">Gate Status Distribution</h3>
                    <GateStatusPieChart data={mockGateStatus} />
                  </div>
                </div>

                {/* Progress Indicators */}
                <div className="bg-gray-50 rounded-lg p-6 space-y-6">
                  <h3 className="text-lg font-semibold">Module Progress</h3>
                  <ProgressIndicator
                    label="GDPR UK Compliance"
                    current={92}
                    total={100}
                    color="#10b981"
                  />
                  <ProgressIndicator
                    label="FCA Regulations"
                    current={88}
                    total={100}
                    color="#3b82f6"
                  />
                  <ProgressIndicator
                    label="Tax Compliance"
                    current={95}
                    total={100}
                    color="#8b5cf6"
                  />
                </div>
              </div>
            )}

            {/* Trends Tab */}
            {activeTab === 'trends' && (
              <div className="bg-gray-50 rounded-lg p-6" ref={trendRef}>
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-lg font-semibold">Risk Trends (Last 7 Days)</h3>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleExport('png', trendRef)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                    >
                      <Download size={18} />
                      Export
                    </button>
                  </div>
                </div>
                <RiskTrendChart data={mockTrendData} height={400} />
              </div>
            )}

            {/* Modules Tab */}
            {activeTab === 'modules' && (
              <div className="space-y-8">
                <div className="bg-gray-50 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-6">Module Performance</h3>
                  <div className="flex justify-center">
                    <ModuleRadarChart data={mockRadarData} size={500} />
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-6">Gate Failure Heatmap</h3>
                  <RiskHeatmap data={mockHeatmapData} width={800} height={300} />
                </div>
              </div>
            )}

            {/* Timeline Tab */}
            {activeTab === 'timeline' && (
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-6">Recent Activity</h3>
                <ComplianceTimeline
                  events={mockTimelineEvents}
                  orientation="vertical"
                  onEventClick={(event) => console.log('Event clicked:', event)}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardExample;
