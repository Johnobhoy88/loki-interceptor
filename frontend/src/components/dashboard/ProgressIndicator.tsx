/**
 * Progress Indicator Widget
 * Animated progress bar with labels and milestones
 */

import React from 'react';
import { motion } from 'framer-motion';
import { PROGRESS_CONFIG, formatPercentage } from '@/utils/chart-config';

export interface ProgressIndicatorProps {
  label: string;
  current: number;
  total: number;
  showPercentage?: boolean;
  showValues?: boolean;
  color?: string;
  height?: number;
  animated?: boolean;
  milestones?: Array<{
    value: number;
    label: string;
  }>;
  className?: string;
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  label,
  current,
  total,
  showPercentage = true,
  showValues = true,
  color = '#0ea5e9',
  height = PROGRESS_CONFIG.height,
  animated = true,
  milestones = [],
  className = '',
}) => {
  const percentage = Math.min((current / total) * 100, 100);

  return (
    <div className={`progress-indicator ${className}`}>
      {/* Label */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-700">{label}</span>
        {showValues && (
          <span className="text-sm text-gray-500">
            {current} / {total}
          </span>
        )}
      </div>

      {/* Progress Bar */}
      <div
        className="relative rounded-full overflow-hidden"
        style={{
          height: `${height}px`,
          backgroundColor: PROGRESS_CONFIG.backgroundColor,
        }}
      >
        <motion.div
          initial={animated ? { width: 0 } : { width: `${percentage}%` }}
          animate={{ width: `${percentage}%` }}
          transition={{
            duration: PROGRESS_CONFIG.transitionDuration / 1000,
            ease: 'easeOut',
          }}
          className="h-full rounded-full"
          style={{
            background: `linear-gradient(90deg, ${color} 0%, ${color}dd 100%)`,
          }}
        />

        {/* Percentage Label */}
        {showPercentage && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="absolute inset-0 flex items-center justify-center"
          >
            <span className="text-xs font-semibold text-white drop-shadow-md">
              {formatPercentage(percentage, 0)}
            </span>
          </motion.div>
        )}

        {/* Milestones */}
        {milestones.map((milestone, index) => {
          const milestonePercentage = (milestone.value / total) * 100;
          return (
            <div
              key={index}
              className="absolute top-0 bottom-0 w-0.5 bg-gray-400"
              style={{ left: `${milestonePercentage}%` }}
              title={milestone.label}
            />
          );
        })}
      </div>

      {/* Milestone Labels */}
      {milestones.length > 0 && (
        <div className="relative mt-2">
          {milestones.map((milestone, index) => {
            const milestonePercentage = (milestone.value / total) * 100;
            return (
              <div
                key={index}
                className="absolute -translate-x-1/2"
                style={{ left: `${milestonePercentage}%` }}
              >
                <div className="text-xs text-gray-500 whitespace-nowrap">
                  {milestone.label}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default ProgressIndicator;
