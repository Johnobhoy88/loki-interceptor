/**
 * Risk Heatmap Visualization
 * Interactive heatmap showing gate failures across modules
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { HEATMAP_CONFIG, getRiskColor } from '@/utils/chart-config';
import { HeatmapCell, RiskLevel } from '@/types';

export interface RiskHeatmapProps {
  data: HeatmapCell[];
  width?: number;
  height?: number;
  cellSize?: number;
  showLabels?: boolean;
  interactive?: boolean;
  onCellClick?: (cell: HeatmapCell) => void;
  className?: string;
}

export const RiskHeatmap: React.FC<RiskHeatmapProps> = ({
  data,
  width = 800,
  height = 400,
  cellSize = HEATMAP_CONFIG.cellSize,
  showLabels = true,
  interactive = true,
  onCellClick,
  className = '',
}) => {
  const [hoveredCell, setHoveredCell] = useState<HeatmapCell | null>(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });

  // Group cells by module
  const moduleGroups = data.reduce((acc, cell) => {
    if (!acc[cell.module_id]) {
      acc[cell.module_id] = [];
    }
    acc[cell.module_id].push(cell);
    return acc;
  }, {} as Record<string, HeatmapCell[]>);

  const modules = Object.keys(moduleGroups);
  const maxGatesPerModule = Math.max(...Object.values(moduleGroups).map((gates) => gates.length));

  const getCellColor = (value: number) => {
    if (value === 0) return getRiskColor(RiskLevel.LOW);
    if (value === 1) return HEATMAP_CONFIG.colorScale.low;
    if (value === 2) return HEATMAP_CONFIG.colorScale.medium;
    return HEATMAP_CONFIG.colorScale.high;
  };

  const getTextColor = (bgColor: string) => {
    // Simple luminance check
    const hex = bgColor.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    return luminance > 0.5 ? HEATMAP_CONFIG.textColor.light : HEATMAP_CONFIG.textColor.dark;
  };

  const handleCellHover = (cell: HeatmapCell | null, event?: React.MouseEvent) => {
    setHoveredCell(cell);
    if (cell && event) {
      setTooltipPos({ x: event.clientX, y: event.clientY });
    }
  };

  return (
    <div className={`risk-heatmap ${className}`} style={{ position: 'relative' }}>
      <svg width={width} height={height} className="heatmap-svg">
        {modules.map((moduleId, moduleIndex) => {
          const gates = moduleGroups[moduleId];
          return (
            <g key={moduleId} transform={`translate(${moduleIndex * (cellSize + HEATMAP_CONFIG.cellGap)}, 40)`}>
              {/* Module label */}
              {showLabels && (
                <text
                  x={cellSize / 2}
                  y={-10}
                  textAnchor="middle"
                  fontSize="12"
                  fill="#475569"
                  fontWeight="600"
                >
                  {moduleId.replace('_', ' ').toUpperCase()}
                </text>
              )}

              {/* Gate cells */}
              {gates.map((cell, gateIndex) => {
                const bgColor = getCellColor(cell.value);
                const textColor = getTextColor(bgColor);

                return (
                  <motion.g
                    key={cell.gate_id}
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: (moduleIndex * gates.length + gateIndex) * 0.02 }}
                  >
                    <rect
                      x={0}
                      y={gateIndex * (cellSize + HEATMAP_CONFIG.cellGap)}
                      width={cellSize}
                      height={cellSize}
                      fill={bgColor}
                      rx={HEATMAP_CONFIG.cellRadius}
                      ry={HEATMAP_CONFIG.cellRadius}
                      style={{
                        cursor: interactive ? 'pointer' : 'default',
                        transition: 'all 0.2s',
                      }}
                      onMouseEnter={(e) => handleCellHover(cell, e)}
                      onMouseLeave={() => handleCellHover(null)}
                      onClick={() => onCellClick && onCellClick(cell)}
                      className={interactive ? 'hover:opacity-80' : ''}
                    />

                    {showLabels && cellSize >= 40 && (
                      <text
                        x={cellSize / 2}
                        y={gateIndex * (cellSize + HEATMAP_CONFIG.cellGap) + cellSize / 2 + 4}
                        textAnchor="middle"
                        fontSize="10"
                        fill={textColor}
                        pointerEvents="none"
                      >
                        {cell.value}
                      </text>
                    )}
                  </motion.g>
                );
              })}
            </g>
          );
        })}
      </svg>

      {/* Tooltip */}
      {hoveredCell && (
        <div
          className="absolute z-50 bg-gray-900 text-white px-4 py-3 rounded-lg shadow-xl pointer-events-none"
          style={{
            left: tooltipPos.x + 10,
            top: tooltipPos.y + 10,
            transform: 'translate(-50%, -100%)',
          }}
        >
          <div className="text-sm font-semibold mb-1">{hoveredCell.label}</div>
          <div className="text-xs text-gray-300">
            Module: {hoveredCell.module_id}
          </div>
          <div className="text-xs text-gray-300">
            Gate: {hoveredCell.gate_id}
          </div>
          <div className="text-xs text-gray-300 mt-1">
            Severity: {hoveredCell.value === 3 ? 'Critical' : hoveredCell.value === 2 ? 'High' : hoveredCell.value === 1 ? 'Medium' : 'Pass'}
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="flex items-center gap-6 mt-6 justify-center">
        <div className="flex items-center gap-2">
          <div
            className="w-4 h-4 rounded"
            style={{ backgroundColor: getRiskColor(RiskLevel.LOW) }}
          />
          <span className="text-sm text-gray-600">Pass</span>
        </div>
        <div className="flex items-center gap-2">
          <div
            className="w-4 h-4 rounded"
            style={{ backgroundColor: HEATMAP_CONFIG.colorScale.low }}
          />
          <span className="text-sm text-gray-600">Low</span>
        </div>
        <div className="flex items-center gap-2">
          <div
            className="w-4 h-4 rounded"
            style={{ backgroundColor: HEATMAP_CONFIG.colorScale.medium }}
          />
          <span className="text-sm text-gray-600">Medium</span>
        </div>
        <div className="flex items-center gap-2">
          <div
            className="w-4 h-4 rounded"
            style={{ backgroundColor: HEATMAP_CONFIG.colorScale.high }}
          />
          <span className="text-sm text-gray-600">Critical</span>
        </div>
      </div>
    </div>
  );
};

export default RiskHeatmap;
