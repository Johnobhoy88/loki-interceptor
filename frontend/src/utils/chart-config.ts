/**
 * Chart Configuration and Theme System
 * Centralized configuration for all chart components
 */

import { RiskLevel } from '@/types';

// Color Palette for Risk Levels
export const RISK_COLORS = {
  [RiskLevel.CRITICAL]: '#ef4444', // red-500
  [RiskLevel.HIGH]: '#f59e0b', // amber-500
  [RiskLevel.MEDIUM]: '#3b82f6', // blue-500
  [RiskLevel.LOW]: '#10b981', // green-500
  [RiskLevel.NONE]: '#6b7280', // gray-500
} as const;

// Gradient Colors for Charts
export const GRADIENT_COLORS = {
  primary: ['#667eea', '#764ba2'],
  success: ['#10b981', '#059669'],
  warning: ['#f59e0b', '#d97706'],
  danger: ['#ef4444', '#dc2626'],
  info: ['#3b82f6', '#2563eb'],
} as const;

// Chart Dimensions
export const CHART_DIMENSIONS = {
  small: { width: 300, height: 200 },
  medium: { width: 500, height: 350 },
  large: { width: 800, height: 500 },
  xlarge: { width: 1200, height: 600 },
} as const;

// Responsive Chart Margins
export const CHART_MARGINS = {
  default: { top: 20, right: 30, bottom: 40, left: 50 },
  compact: { top: 10, right: 20, bottom: 30, left: 40 },
  spacious: { top: 30, right: 50, bottom: 60, left: 70 },
} as const;

// Font Configuration
export const CHART_FONTS = {
  family: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  sizes: {
    tiny: 10,
    small: 12,
    medium: 14,
    large: 16,
    xlarge: 20,
  },
  weights: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
} as const;

// Animation Configuration
export const ANIMATION_CONFIG = {
  duration: 750,
  easing: 'ease-in-out',
  delay: 0,
  stagger: 50,
} as const;

// Tooltip Configuration
export const TOOLTIP_CONFIG = {
  backgroundColor: '#1e293b',
  textColor: '#ffffff',
  borderRadius: 8,
  padding: 12,
  fontSize: 13,
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
} as const;

// Legend Configuration
export const LEGEND_CONFIG = {
  iconSize: 14,
  iconType: 'circle',
  layout: 'horizontal',
  verticalAlign: 'bottom',
  align: 'center',
  wrapperStyle: {
    paddingTop: 20,
  },
} as const;

// Grid Configuration
export const GRID_CONFIG = {
  strokeDasharray: '3 3',
  stroke: '#e2e8f0',
  opacity: 0.5,
} as const;

// Axis Configuration
export const AXIS_CONFIG = {
  stroke: '#94a3b8',
  strokeWidth: 1,
  tick: {
    fill: '#64748b',
    fontSize: 12,
  },
  label: {
    fill: '#475569',
    fontSize: 14,
    fontWeight: 600,
  },
} as const;

// Gauge Chart Configuration
export const GAUGE_CONFIG = {
  startAngle: -90,
  endAngle: 90,
  innerRadius: '75%',
  outerRadius: '100%',
  cornerRadius: 10,
  ranges: [
    { min: 0, max: 25, color: RISK_COLORS[RiskLevel.CRITICAL], label: 'Critical' },
    { min: 25, max: 50, color: RISK_COLORS[RiskLevel.HIGH], label: 'High Risk' },
    { min: 50, max: 75, color: RISK_COLORS[RiskLevel.MEDIUM], label: 'Medium' },
    { min: 75, max: 100, color: RISK_COLORS[RiskLevel.LOW], label: 'Good' },
  ],
} as const;

// Heatmap Configuration
export const HEATMAP_CONFIG = {
  cellSize: 50,
  cellGap: 2,
  cellRadius: 4,
  colorScale: {
    low: '#d1fae5',
    medium: '#fef3c7',
    high: '#fee2e2',
  },
  textColor: {
    light: '#1e293b',
    dark: '#ffffff',
  },
} as const;

// Progress Bar Configuration
export const PROGRESS_CONFIG = {
  height: 24,
  borderRadius: 12,
  backgroundColor: '#e2e8f0',
  transitionDuration: 500,
} as const;

// Timeline Configuration
export const TIMELINE_CONFIG = {
  lineColor: '#cbd5e1',
  lineWidth: 2,
  dotSize: 12,
  spacing: 60,
  colors: {
    validation: '#3b82f6',
    correction: '#10b981',
    alert: '#f59e0b',
    audit: '#8b5cf6',
  },
} as const;

// Accessible Color Palette (WCAG AA compliant)
export const ACCESSIBLE_COLORS = [
  '#0369a1', // blue-700
  '#047857', // green-700
  '#b45309', // amber-700
  '#c026d3', // fuchsia-600
  '#7c2d12', // orange-900
  '#be123c', // rose-700
  '#4338ca', // indigo-700
  '#0891b2', // cyan-600
] as const;

// Export preset configurations for common chart types
export const CHART_PRESETS = {
  lineChart: {
    margin: CHART_MARGINS.default,
    stroke: GRADIENT_COLORS.primary[0],
    strokeWidth: 2,
    dot: { r: 4, fill: GRADIENT_COLORS.primary[1] },
    activeDot: { r: 6 },
    animationDuration: ANIMATION_CONFIG.duration,
  },
  barChart: {
    margin: CHART_MARGINS.default,
    fill: GRADIENT_COLORS.primary[0],
    radius: [8, 8, 0, 0],
    animationDuration: ANIMATION_CONFIG.duration,
  },
  pieChart: {
    innerRadius: 0,
    outerRadius: 80,
    paddingAngle: 2,
    cornerRadius: 4,
    animationDuration: ANIMATION_CONFIG.duration,
  },
  areaChart: {
    margin: CHART_MARGINS.default,
    fill: 'url(#colorGradient)',
    stroke: GRADIENT_COLORS.primary[0],
    strokeWidth: 2,
    fillOpacity: 0.6,
    animationDuration: ANIMATION_CONFIG.duration,
  },
  radarChart: {
    outerRadius: 120,
    stroke: GRADIENT_COLORS.primary[0],
    fill: GRADIENT_COLORS.primary[0],
    fillOpacity: 0.3,
    animationDuration: ANIMATION_CONFIG.duration,
  },
} as const;

// Utility function to get risk color
export const getRiskColor = (risk: RiskLevel | string): string => {
  const riskLevel = risk.toUpperCase() as RiskLevel;
  return RISK_COLORS[riskLevel] || RISK_COLORS[RiskLevel.NONE];
};

// Utility function to get gradient definition
export const getGradientDef = (id: string, colors: readonly string[]) => {
  return {
    id,
    type: 'linear' as const,
    x1: '0%',
    y1: '0%',
    x2: '0%',
    y2: '100%',
    stops: [
      { offset: '0%', stopColor: colors[0], stopOpacity: 0.8 },
      { offset: '100%', stopColor: colors[1], stopOpacity: 0.2 },
    ],
  };
};

// Utility function to format large numbers
export const formatNumber = (num: number): string => {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toString();
};

// Utility function to format percentage
export const formatPercentage = (value: number, decimals = 1): string => {
  return `${value.toFixed(decimals)}%`;
};

// Utility function to calculate compliance score grade
export const getComplianceGrade = (score: number): 'A+' | 'A' | 'B' | 'C' | 'D' | 'F' => {
  if (score >= 97) return 'A+';
  if (score >= 90) return 'A';
  if (score >= 80) return 'B';
  if (score >= 70) return 'C';
  if (score >= 60) return 'D';
  return 'F';
};

// Utility function to get status color
export const getStatusColor = (status: string): string => {
  const statusMap: Record<string, string> = {
    pass: RISK_COLORS[RiskLevel.LOW],
    fail: RISK_COLORS[RiskLevel.CRITICAL],
    warning: RISK_COLORS[RiskLevel.HIGH],
    skip: RISK_COLORS[RiskLevel.NONE],
    error: RISK_COLORS[RiskLevel.CRITICAL],
  };
  return statusMap[status.toLowerCase()] || RISK_COLORS[RiskLevel.NONE];
};

export default {
  RISK_COLORS,
  GRADIENT_COLORS,
  CHART_DIMENSIONS,
  CHART_MARGINS,
  CHART_FONTS,
  ANIMATION_CONFIG,
  TOOLTIP_CONFIG,
  LEGEND_CONFIG,
  GRID_CONFIG,
  AXIS_CONFIG,
  GAUGE_CONFIG,
  HEATMAP_CONFIG,
  PROGRESS_CONFIG,
  TIMELINE_CONFIG,
  ACCESSIBLE_COLORS,
  CHART_PRESETS,
  getRiskColor,
  getGradientDef,
  formatNumber,
  formatPercentage,
  getComplianceGrade,
  getStatusColor,
};
