/**
 * Gate Status Pie Chart
 * Visual breakdown of gate pass/fail/warning statistics
 */

import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { motion } from 'framer-motion';
import { getStatusColor } from '@/utils/chart-config';

export interface GateStatusData {
  name: string;
  value: number;
}

export interface GateStatusPieChartProps {
  data: GateStatusData[];
  size?: number;
  innerRadius?: number;
  showLegend?: boolean;
  showLabels?: boolean;
  animated?: boolean;
  className?: string;
}

export const GateStatusPieChart: React.FC<GateStatusPieChartProps> = ({
  data,
  size = 300,
  innerRadius = 60,
  showLegend = true,
  showLabels = true,
  animated = true,
  className = '',
}) => {
  const COLORS = data.map((entry) => getStatusColor(entry.name));

  const renderCustomLabel = (entry: any) => {
    const percent = ((entry.value / entry.payload.totalValue) * 100).toFixed(0);
    return `${percent}%`;
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      const total = payload[0].payload.totalValue;
      const percent = ((data.value / total) * 100).toFixed(1);

      return (
        <div className="bg-gray-900 text-white px-4 py-3 rounded-lg shadow-lg">
          <p className="font-semibold mb-1">{data.name}</p>
          <div className="text-sm">
            <div className="flex justify-between gap-4">
              <span className="text-gray-300">Count:</span>
              <span className="font-bold">{data.value}</span>
            </div>
            <div className="flex justify-between gap-4 mt-1">
              <span className="text-gray-300">Percentage:</span>
              <span className="font-bold">{percent}%</span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  // Calculate total for percentage calculations
  const totalValue = data.reduce((sum, entry) => sum + entry.value, 0);
  const dataWithTotal = data.map((entry) => ({ ...entry, totalValue }));

  return (
    <motion.div
      initial={animated ? { opacity: 0, scale: 0.8 } : false}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className={`gate-status-pie ${className}`}
    >
      <ResponsiveContainer width={size} height={size}>
        <PieChart>
          <Pie
            data={dataWithTotal}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={showLabels ? renderCustomLabel : false}
            outerRadius={size * 0.35}
            innerRadius={innerRadius}
            fill="#8884d8"
            dataKey="value"
            animationBegin={0}
            animationDuration={animated ? 800 : 0}
          >
            {dataWithTotal.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          {showLegend && (
            <Legend
              verticalAlign="bottom"
              height={36}
              iconType="circle"
              formatter={(value, entry: any) => `${value} (${entry.payload.value})`}
            />
          )}
        </PieChart>
      </ResponsiveContainer>

      {/* Center label */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="text-center">
          <div className="text-3xl font-bold text-gray-700">{totalValue}</div>
          <div className="text-sm text-gray-500">Total Gates</div>
        </div>
      </div>
    </motion.div>
  );
};

export default GateStatusPieChart;
