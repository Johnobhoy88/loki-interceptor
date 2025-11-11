/**
 * Compliance Timeline Visualization
 * Interactive timeline showing validation and correction events
 */

import React from 'react';
import { motion } from 'framer-motion';
import { format, parseISO } from 'date-fns';
import { AlertCircle, CheckCircle, AlertTriangle, FileText } from 'lucide-react';
import { TimelineEvent, RiskLevel } from '@/types';
import { TIMELINE_CONFIG, getRiskColor } from '@/utils/chart-config';

export interface ComplianceTimelineProps {
  events: TimelineEvent[];
  maxEvents?: number;
  orientation?: 'vertical' | 'horizontal';
  animated?: boolean;
  onEventClick?: (event: TimelineEvent) => void;
  className?: string;
}

const EVENT_ICONS = {
  validation: FileText,
  correction: CheckCircle,
  alert: AlertTriangle,
  audit: AlertCircle,
};

export const ComplianceTimeline: React.FC<ComplianceTimelineProps> = ({
  events,
  maxEvents = 20,
  orientation = 'vertical',
  animated = true,
  onEventClick,
  className = '',
}) => {
  const displayEvents = events.slice(0, maxEvents);

  const getEventColor = (event: TimelineEvent) => {
    if (event.event_type in TIMELINE_CONFIG.colors) {
      return TIMELINE_CONFIG.colors[event.event_type as keyof typeof TIMELINE_CONFIG.colors];
    }
    return getRiskColor(event.risk_level);
  };

  if (orientation === 'vertical') {
    return (
      <div className={`compliance-timeline ${className}`}>
        <div className="relative">
          {/* Timeline line */}
          <div
            className="absolute left-6 top-0 bottom-0 w-0.5"
            style={{
              backgroundColor: TIMELINE_CONFIG.lineColor,
            }}
          />

          {/* Events */}
          <div className="space-y-8">
            {displayEvents.map((event, index) => {
              const Icon = EVENT_ICONS[event.event_type] || FileText;
              const color = getEventColor(event);

              return (
                <motion.div
                  key={event.id}
                  initial={animated ? { opacity: 0, x: -20 } : false}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1, duration: 0.5 }}
                  className="relative pl-16"
                >
                  {/* Dot */}
                  <div
                    className="absolute left-3 top-2 w-6 h-6 rounded-full border-4 border-white shadow-md flex items-center justify-center"
                    style={{ backgroundColor: color }}
                  >
                    <Icon size={12} color="white" />
                  </div>

                  {/* Event card */}
                  <div
                    className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-4 cursor-pointer border-l-4"
                    style={{ borderLeftColor: color }}
                    onClick={() => onEventClick && onEventClick(event)}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="text-sm font-semibold text-gray-800">
                        {event.title}
                      </h4>
                      <span className="text-xs text-gray-500 whitespace-nowrap ml-4">
                        {format(parseISO(event.timestamp), 'MMM dd, HH:mm')}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">{event.description}</p>
                    {event.metadata && Object.keys(event.metadata).length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-2">
                        {Object.entries(event.metadata).slice(0, 3).map(([key, value]) => (
                          <span
                            key={key}
                            className="inline-flex items-center px-2 py-1 rounded-md bg-gray-100 text-xs text-gray-700"
                          >
                            {key}: {String(value)}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  // Horizontal orientation
  return (
    <div className={`compliance-timeline-horizontal ${className}`}>
      <div className="relative pb-16">
        {/* Timeline line */}
        <div
          className="absolute top-6 left-0 right-0 h-0.5"
          style={{
            backgroundColor: TIMELINE_CONFIG.lineColor,
          }}
        />

        {/* Events */}
        <div className="flex gap-4 overflow-x-auto">
          {displayEvents.map((event, index) => {
            const Icon = EVENT_ICONS[event.event_type] || FileText;
            const color = getEventColor(event);

            return (
              <motion.div
                key={event.id}
                initial={animated ? { opacity: 0, y: 20 } : false}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1, duration: 0.5 }}
                className="relative pt-16 min-w-[200px]"
              >
                {/* Dot */}
                <div
                  className="absolute left-1/2 top-3 -translate-x-1/2 w-6 h-6 rounded-full border-4 border-white shadow-md flex items-center justify-center"
                  style={{ backgroundColor: color }}
                >
                  <Icon size={12} color="white" />
                </div>

                {/* Event card */}
                <div
                  className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-3 cursor-pointer border-t-4"
                  style={{ borderTopColor: color }}
                  onClick={() => onEventClick && onEventClick(event)}
                >
                  <div className="text-xs text-gray-500 mb-1">
                    {format(parseISO(event.timestamp), 'MMM dd')}
                  </div>
                  <h4 className="text-sm font-semibold text-gray-800 mb-1">
                    {event.title}
                  </h4>
                  <p className="text-xs text-gray-600 line-clamp-2">
                    {event.description}
                  </p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ComplianceTimeline;
