import React, { useState } from 'react';
import { Correction } from '@/types/editor';

interface CorrectionAnnotationProps {
  corrections: Correction[];
}

export const CorrectionAnnotation: React.FC<CorrectionAnnotationProps> = ({
  corrections,
}) => {
  const [expanded, setExpanded] = useState(false);

  if (corrections.length === 0) return null;

  const getTypeIcon = (type: string) => {
    const icons: Record<string, string> = {
      grammar: '📝',
      spelling: '✏️',
      style: '🎨',
      punctuation: '❗',
      clarity: '💡',
      consistency: '🔄',
      compliance: '✓',
      accessibility: '♿',
    };
    return icons[type] || '•';
  };

  const getConfidenceClass = (confidence: number) => {
    if (confidence >= 0.9) return 'high';
    if (confidence >= 0.7) return 'medium';
    return 'low';
  };

  return (
    <div className="correction-annotation">
      <div
        className="annotation-header"
        onClick={() => setExpanded(!expanded)}
      >
        <span className="annotation-count">
          {corrections.length} correction{corrections.length !== 1 ? 's' : ''}
        </span>
        <span className="expand-icon">{expanded ? '▼' : '▶'}</span>
      </div>
      {expanded && (
        <div className="annotation-details">
          {corrections.map((correction) => (
            <div key={correction.id} className="correction-detail">
              <div className="correction-info">
                <span className="type-icon">
                  {getTypeIcon(correction.type)}
                </span>
                <span className="type-name">{correction.type}</span>
                <span
                  className={`confidence ${getConfidenceClass(
                    correction.confidence
                  )}`}
                >
                  {(correction.confidence * 100).toFixed(0)}%
                </span>
              </div>
              <div className="correction-text-change">
                <span className="original-text">{correction.original}</span>
                <span className="arrow">→</span>
                <span className="corrected-text">{correction.corrected}</span>
              </div>
              <p className="correction-explanation">
                {correction.explanation}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
