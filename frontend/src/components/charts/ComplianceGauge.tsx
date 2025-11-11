/**
 * Compliance Gauge Chart
 * Interactive gauge displaying overall compliance score with grade indicator
 */

import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { motion } from 'framer-motion';
import { GAUGE_CONFIG, getRiskColor, getComplianceGrade } from '@/utils/chart-config';
import { RiskLevel } from '@/types';

export interface ComplianceGaugeProps {
  score: number; // 0-100
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  showGrade?: boolean;
  showPercentage?: boolean;
  animated?: boolean;
  className?: string;
}

const SIZE_CONFIG = {
  sm: { width: 200, height: 150, fontSize: 24 },
  md: { width: 300, height: 225, fontSize: 36 },
  lg: { width: 400, height: 300, fontSize: 48 },
};

export const ComplianceGauge: React.FC<ComplianceGaugeProps> = ({
  score,
  label = 'Compliance Score',
  size = 'md',
  showGrade = true,
  showPercentage = true,
  animated = true,
  className = '',
}) => {
  const config = SIZE_CONFIG[size];
  const grade = getComplianceGrade(score);

  // Determine color based on score
  const getColor = () => {
    if (score >= 90) return getRiskColor(RiskLevel.LOW);
    if (score >= 75) return getRiskColor(RiskLevel.MEDIUM);
    if (score >= 60) return getRiskColor(RiskLevel.HIGH);
    return getRiskColor(RiskLevel.CRITICAL);
  };

  // Create gauge data
  const gaugeData = [
    { value: score, fill: getColor() },
    { value: 100 - score, fill: '#e2e8f0' },
  ];

  return (
    <div className={`compliance-gauge ${className}`}>
      <div className="text-center mb-4">
        <h3 className="text-lg font-semibold text-gray-700">{label}</h3>
      </div>

      <ResponsiveContainer width={config.width} height={config.height}>
        <PieChart>
          <Pie
            data={gaugeData}
            cx="50%"
            cy="50%"
            startAngle={180}
            endAngle={0}
            innerRadius={config.width * 0.25}
            outerRadius={config.width * 0.35}
            paddingAngle={0}
            dataKey="value"
            animationBegin={0}
            animationDuration={animated ? 1000 : 0}
            animationEasing="ease-out"
          >
            {gaugeData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>

      <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
        {showPercentage && (
          <motion.div
            initial={animated ? { opacity: 0, scale: 0.5 } : false}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5, duration: 0.5 }}
            className="text-center"
          >
            <div
              style={{ fontSize: config.fontSize, color: getColor() }}
              className="font-bold leading-none"
            >
              {Math.round(score)}
            </div>
            <div className="text-sm text-gray-500 mt-1">out of 100</div>
          </motion.div>
        )}

        {showGrade && (
          <motion.div
            initial={animated ? { opacity: 0, y: 20 } : false}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.5 }}
            className="mt-4"
          >
            <div className="inline-flex items-center px-4 py-2 bg-white rounded-lg shadow-md border-2"
                 style={{ borderColor: getColor() }}>
              <span className="text-2xl font-bold" style={{ color: getColor() }}>
                {grade}
              </span>
              <span className="ml-2 text-sm text-gray-600">Grade</span>
            </div>
          </motion.div>
        )}
      </div>

      <style jsx>{`
        .compliance-gauge {
          position: relative;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 1rem;
        }
      `}</style>
    </div>
  );
};

export default ComplianceGauge;
