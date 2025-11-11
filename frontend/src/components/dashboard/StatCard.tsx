/**
 * Stat Card Widget
 * KPI display card with trend indicator
 */

import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { formatNumber } from '@/utils/chart-config';

export interface StatCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  trend?: {
    direction: 'up' | 'down' | 'neutral';
    value: number;
    label?: string;
  };
  icon?: React.ReactNode;
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'info';
  animated?: boolean;
  className?: string;
}

const COLOR_SCHEMES = {
  primary: {
    bg: 'bg-blue-50',
    text: 'text-blue-600',
    border: 'border-blue-200',
  },
  success: {
    bg: 'bg-green-50',
    text: 'text-green-600',
    border: 'border-green-200',
  },
  warning: {
    bg: 'bg-amber-50',
    text: 'text-amber-600',
    border: 'border-amber-200',
  },
  danger: {
    bg: 'bg-red-50',
    text: 'text-red-600',
    border: 'border-red-200',
  },
  info: {
    bg: 'bg-cyan-50',
    text: 'text-cyan-600',
    border: 'border-cyan-200',
  },
};

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  trend,
  icon,
  color = 'primary',
  animated = true,
  className = '',
}) => {
  const colorScheme = COLOR_SCHEMES[color];

  const TrendIcon = trend
    ? trend.direction === 'up'
      ? TrendingUp
      : trend.direction === 'down'
      ? TrendingDown
      : Minus
    : null;

  const trendColor =
    trend?.direction === 'up'
      ? 'text-green-600'
      : trend?.direction === 'down'
      ? 'text-red-600'
      : 'text-gray-600';

  return (
    <motion.div
      initial={animated ? { opacity: 0, y: 20 } : false}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.3 }}
      className={`stat-card bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow border-2 ${colorScheme.border} ${className}`}
    >
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="text-sm font-medium text-gray-600 uppercase tracking-wide">
              {title}
            </h3>
          </div>
          {icon && (
            <div className={`p-3 rounded-lg ${colorScheme.bg}`}>
              <div className={colorScheme.text}>{icon}</div>
            </div>
          )}
        </div>

        {/* Value */}
        <div className="mb-2">
          <div className={`text-4xl font-bold ${colorScheme.text}`}>
            {typeof value === 'number' ? formatNumber(value) : value}
          </div>
          {subtitle && (
            <div className="text-sm text-gray-500 mt-1">{subtitle}</div>
          )}
        </div>

        {/* Trend */}
        {trend && TrendIcon && (
          <div className={`flex items-center gap-2 text-sm ${trendColor}`}>
            <TrendIcon size={16} />
            <span className="font-semibold">{trend.value}%</span>
            {trend.label && (
              <span className="text-gray-500">{trend.label}</span>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default StatCard;
