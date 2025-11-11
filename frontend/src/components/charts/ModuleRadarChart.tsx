/**
 * Module Comparison Radar Chart
 * Interactive radar chart for comparing module performance
 */

import React from 'react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts';
import { motion } from 'framer-motion';
import { CHART_PRESETS, GRADIENT_COLORS } from '@/utils/chart-config';
import { RadarChartData } from '@/types';

export interface ModuleRadarChartProps {
  data: RadarChartData[];
  size?: number;
  showGrid?: boolean;
  showLegend?: boolean;
  animated?: boolean;
  fillOpacity?: number;
  className?: string;
}

export const ModuleRadarChart: React.FC<ModuleRadarChartProps> = ({
  data,
  size = 400,
  showGrid = true,
  showLegend = false,
  animated = true,
  fillOpacity = 0.6,
  className = '',
}) => {
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-gray-900 text-white px-4 py-3 rounded-lg shadow-lg">
          <p className="font-semibold mb-1">{data.module}</p>
          <div className="text-sm">
            <span className="text-gray-300">Score: </span>
            <span className="font-bold">{data.score}</span>
            <span className="text-gray-400"> / {data.fullMark}</span>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div
      initial={animated ? { opacity: 0, scale: 0.9 } : false}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6 }}
      className={className}
    >
      <ResponsiveContainer width={size} height={size}>
        <RadarChart data={data} margin={{ top: 20, right: 30, bottom: 20, left: 30 }}>
          {showGrid && (
            <PolarGrid
              stroke="#cbd5e1"
              strokeDasharray="3 3"
            />
          )}

          <PolarAngleAxis
            dataKey="module"
            tick={{ fill: '#64748b', fontSize: 12 }}
            stroke="#94a3b8"
          />

          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: '#64748b', fontSize: 10 }}
            stroke="#94a3b8"
          />

          <Tooltip content={<CustomTooltip />} />

          {showLegend && (
            <Legend
              verticalAlign="bottom"
              height={36}
            />
          )}

          <Radar
            name="Compliance Score"
            dataKey="score"
            stroke={GRADIENT_COLORS.primary[0]}
            fill={GRADIENT_COLORS.primary[0]}
            fillOpacity={fillOpacity}
            animationDuration={animated ? 1000 : 0}
            animationBegin={200}
          />
        </RadarChart>
      </ResponsiveContainer>

      {/* Score legend */}
      <div className="mt-4 text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-gray-50 rounded-lg">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: GRADIENT_COLORS.primary[0] }}
          />
          <span className="text-sm text-gray-600">Module Performance Score</span>
        </div>
      </div>
    </motion.div>
  );
};

export default ModuleRadarChart;
