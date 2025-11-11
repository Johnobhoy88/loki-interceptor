/**
 * Risk Trend Chart
 * Line/Area chart showing risk trends over time
 */

import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { motion } from 'framer-motion';
import { RISK_COLORS, CHART_PRESETS, AXIS_CONFIG, GRID_CONFIG } from '@/utils/chart-config';
import { RiskLevel } from '@/types';

export interface RiskTrendData {
  date: string;
  Critical: number;
  High: number;
  Medium: number;
  Low: number;
  total: number;
}

export interface RiskTrendChartProps {
  data: RiskTrendData[];
  height?: number;
  showLegend?: boolean;
  showGrid?: boolean;
  stacked?: boolean;
  animated?: boolean;
  className?: string;
}

export const RiskTrendChart: React.FC<RiskTrendChartProps> = ({
  data,
  height = 350,
  showLegend = true,
  showGrid = true,
  stacked = true,
  animated = true,
  className = '',
}) => {
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-900 text-white p-4 rounded-lg shadow-lg border border-gray-700">
          <p className="font-semibold mb-2">{label}</p>
          {payload.map((entry: any, index: number) => (
            <div key={`item-${index}`} className="flex items-center justify-between gap-4 text-sm">
              <span style={{ color: entry.color }}>{entry.name}:</span>
              <span className="font-bold">{entry.value}</span>
            </div>
          ))}
          <div className="mt-2 pt-2 border-t border-gray-700">
            <div className="flex items-center justify-between text-sm">
              <span>Total:</span>
              <span className="font-bold">
                {payload.reduce((sum: number, entry: any) => sum + entry.value, 0)}
              </span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div
      initial={animated ? { opacity: 0, y: 20 } : false}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={className}
    >
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart
          data={data}
          margin={CHART_PRESETS.areaChart.margin}
        >
          {showGrid && (
            <CartesianGrid
              strokeDasharray={GRID_CONFIG.strokeDasharray}
              stroke={GRID_CONFIG.stroke}
              opacity={GRID_CONFIG.opacity}
            />
          )}

          <XAxis
            dataKey="date"
            stroke={AXIS_CONFIG.stroke}
            tick={AXIS_CONFIG.tick}
            style={{ fontSize: 12 }}
          />

          <YAxis
            stroke={AXIS_CONFIG.stroke}
            tick={AXIS_CONFIG.tick}
            label={{
              value: 'Number of Validations',
              angle: -90,
              position: 'insideLeft',
              style: { fontSize: 12, fill: '#64748b' },
            }}
          />

          <Tooltip content={<CustomTooltip />} />

          {showLegend && (
            <Legend
              verticalAlign="top"
              height={36}
              iconType="circle"
              wrapperStyle={{ paddingBottom: 20 }}
            />
          )}

          <defs>
            <linearGradient id="colorCritical" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={RISK_COLORS[RiskLevel.CRITICAL]} stopOpacity={0.8} />
              <stop offset="95%" stopColor={RISK_COLORS[RiskLevel.CRITICAL]} stopOpacity={0.1} />
            </linearGradient>
            <linearGradient id="colorHigh" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={RISK_COLORS[RiskLevel.HIGH]} stopOpacity={0.8} />
              <stop offset="95%" stopColor={RISK_COLORS[RiskLevel.HIGH]} stopOpacity={0.1} />
            </linearGradient>
            <linearGradient id="colorMedium" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={RISK_COLORS[RiskLevel.MEDIUM]} stopOpacity={0.8} />
              <stop offset="95%" stopColor={RISK_COLORS[RiskLevel.MEDIUM]} stopOpacity={0.1} />
            </linearGradient>
            <linearGradient id="colorLow" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={RISK_COLORS[RiskLevel.LOW]} stopOpacity={0.8} />
              <stop offset="95%" stopColor={RISK_COLORS[RiskLevel.LOW]} stopOpacity={0.1} />
            </linearGradient>
          </defs>

          <Area
            type="monotone"
            dataKey="Critical"
            stackId="1"
            stroke={RISK_COLORS[RiskLevel.CRITICAL]}
            fill="url(#colorCritical)"
            animationDuration={animated ? 1000 : 0}
          />
          <Area
            type="monotone"
            dataKey="High"
            stackId="1"
            stroke={RISK_COLORS[RiskLevel.HIGH]}
            fill="url(#colorHigh)"
            animationDuration={animated ? 1000 : 0}
          />
          <Area
            type="monotone"
            dataKey="Medium"
            stackId="1"
            stroke={RISK_COLORS[RiskLevel.MEDIUM]}
            fill="url(#colorMedium)"
            animationDuration={animated ? 1000 : 0}
          />
          <Area
            type="monotone"
            dataKey="Low"
            stackId="1"
            stroke={RISK_COLORS[RiskLevel.LOW]}
            fill="url(#colorLow)"
            animationDuration={animated ? 1000 : 0}
          />
        </AreaChart>
      </ResponsiveContainer>
    </motion.div>
  );
};

export default RiskTrendChart;
